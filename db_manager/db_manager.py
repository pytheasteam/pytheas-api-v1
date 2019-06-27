import json
from datetime import datetime as dt, datetime

import requests
from flask import jsonify
import jwt

from db_manager.config.agent_url import AGENT_ENDPOINT, AGENT_ATTRACTION_GET, AGENT_TAGS_GET
from db_manager.config.secrets import SERVER_SECRET_KEY, PROFILE_REMOVE_SP, PROFILE_RATE_SET_SP, TRIP_UPDATE_RSRV_SP, UPSERT_TRIP_FLIGHT_SP
from db_manager.config.exteranl_apis import FLIGHTS_BASE_ENDPOINT, HOTELS_BASE_ENDPOINT, HOTELS_HEADER
from db_manager.location_code_matcher import LocationMatcher
from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.tag_attraction import TagAttraction
from api.models.trip import Trip, TripAttraction
from api.models.user import User
from api.models.user_trip_profile import UserProfile, ProfileTag
from api.models.hotel import Hotel, TripHotel
from api.models.flight import TripFlight
from db_manager.pytheas_db_manager_base import PytheasDBManagerBase
from trip_builder.city_trip_builder import CityWalkTripBuilder
from trip_builder.routes_builder.basic_route_builder import BasicRoutesBuilder
from trip_builder.routes_builder.dfs_routes_builder import DFSRoutesBuilder


class SQLPytheasManager(PytheasDBManagerBase):
    # TODO: Refactor exceptions handling

    def __init__(self, db):
        super().__init__(db)

    def initialize(self):
        self.db.create_all()
        self.db.session.commit()
        return "success", 200

    @staticmethod
    def serialize_result(elements):
        serialized_result = []
        if type(elements) is not list:
            elements = [elements]
        for element in elements:
            element = vars(element)
            fields = {}
            for field in [x for x in list(element.keys()) if not x.startswith('_') and x != 'metadata']:
                data = element[field]
                try:
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            serialized_result.append(fields)
        return jsonify(serialized_result)

    #  CREATES FUNCTIONS
    def _create(self, model, **kwargs):
        try:
            new_model = model(**kwargs)
            self.db.session.add(new_model)
            self.db.session.commit()
            return new_model, 200
        except Exception as e:
            return f"Error creating {model}: {e}", 500

    def create_user(self, username, full_name, email, google_token):
        email_exist = User.query.filter_by(email=email).first()
        username_exist = User.query.filter_by(username=username).first()
        if not email_exist and not username_exist:
            new_user, status = self._create(
                User,
                id=None,
                username=username,
                full_name=full_name,
                created=dt.now(),
                email=email,
                google_token=google_token
            )
            if status is not 200:
                return new_user, status
        return jsonify({"token": jwt.encode({'username': username}, SERVER_SECRET_KEY, algorithm='HS256').decode('utf8')}), 200

    def create_tag(self, tag_name):
        return self._create(
            Tag,
            name=tag_name
        )

    def create_attraction(self, name, rate, address, price, description, phone, website, city_id, attraction_id=None):
        return self._create(
            Attraction,
            id=attraction_id,
            name=name,
            rate=rate,
            address=address,
            price=price,
            description=description,
            phone_number=phone,
            website=website,
            city_id=city_id
        )

    def create_city(self, name, country, city_id=None):
        return self._create(
            City,
            name=name,
            country=country,
            id=city_id
        )

    def create_profile(self, username, profile_name, tags):

        try:
            # get tags id from name
            user = User.query.filter_by(username=username).first()
            # create new profile
            new_profile = UserProfile(
                user_id=user.id,
                name=profile_name
            )
            self.db.session.add(new_profile)
            self.db.session.commit()

            # create tags
            for tag in tags:
                db_tag = Tag.query.filter_by(name=tag).first()
                if db_tag:
                    new_profile_tag = ProfileTag(
                        tag_id=db_tag.id,
                        profile_id=new_profile.id
                    )
                    self.db.session.add(new_profile_tag)
                    self.db.session.commit()
        except Exception as e:
            print(e)
            self.db.session.rollback()
            return "Error creating new profile", 500
        else:
            return "success", 200

    def upsert_trip(self, username, profile_id, flight_rsrv, hotel_rsrv_code, trip_data):
        trip_id = int(trip_data['id'])
        trip = None
        if trip_id is not None and trip_id > 0:
            trip = Trip.query.filter_by(id=trip_id).first()

        if trip is None:
            return self.create_trip(username, profile_id, flight_rsrv, hotel_rsrv_code, trip_data)
        else:
            return self.update_trip(username, trip_id, flight_rsrv, hotel_rsrv_code)

    def create_trip(self, username, profile_id, flight_rsrv, hotel_rsrv_code, trip_data):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, id=profile_id).first().id
            if profile_id is None:
                raise

            city_id = City.query.filter_by(name=trip_data['destination']).first().id
            if flight_rsrv is None or flight_rsrv == {} or hotel_rsrv_code is None:
                is_booked = False
            else:
                is_booked = True

            new_trip = Trip(
                user_id=user_id,
                profile_id=profile_id,
                currency=trip_data['currency'],
                price=int(trip_data['price']),
                days=int(trip_data['days']),
                start_date=datetime.strptime(trip_data['start_date'], '%d/%m/%Y'),
                end_date=datetime.strptime(trip_data['end_date'], '%d/%m/%Y'),
                is_booked=is_booked,
                people_number=int(trip_data['people_number']),
                city_id=city_id,
                hotel_rsrv_code=hotel_rsrv_code
            )
            self.db.session.add(new_trip)
            self.db.session.commit()

            if flight_rsrv is not None and flight_rsrv != {}:
                self._upsert_trip_flight(new_trip.id, flight_rsrv)

            attractions = self._add_trip_attractions(trip_data, new_trip)
            self._create_hotel(new_trip.id, trip_data['hotel'])
            return_trip = self._get_trip(new_trip.id)
            return return_trip, 200
        except Exception as e:
            print(e)
            self.db.session.rollback()
            return "Error creating new profile", 500

    def _add_trip_attractions(self, trip_full_data, trip):
        try:
            for day in range(0, len(trip_full_data['places'])):
                for i in range(1, len(trip_full_data['places'][day])):
                    attraction = trip_full_data['places'][day][i]
                    if attraction is None or attraction=={}:
                        continue
                    new_trip_attraction = TripAttraction(
                        trip_id=trip.id,
                        attraction_id=attraction['id'],
                        day=day + 1
                    )
                    self.db.session.add(new_trip_attraction)
                    self.db.session.commit()
        except Exception as e:
            print(e)
            self.db.session.rollback()
            raise

    def _create_hotel(self, trip_id, hotel_data):
        hotel_id = 0
        hotel_name = hotel_data['name']
        hotel_url = hotel_data['url']
        hotel = Hotel.query.filter_by(name=hotel_name, url=hotel_url).first()
        if hotel is None:
            new_hotel = Hotel(
                name=hotel_name,
                address=hotel_data['address'],
                main_photo_url=hotel_data['main_photo_url'],
                stars=hotel_data['stars'],
                url=hotel_url,
                description=hotel_data['description'],
                facilities=""
            )
            self.db.session.add(new_hotel)
            self.db.session.commit()
            hotel_id = new_hotel.id
        else:
            hotel_id = hotel.id

        #Insert trip-hotel
        new_trip_hotel = TripHotel(
            trip_id=trip_id,
            hotel_id=hotel_id,
            start_date=hotel_data['start_date'],
            end_date=hotel_data['end_date'],
            price_per_night=int(hotel_data['price_per_night']),
            room_type=hotel_data['room_type'],
            currency=hotel_data['currency'],
        )
        self.db.session.add(new_trip_hotel)
        self.db.session.commit()

    def update_trip(self, username, trip_id, flight_rsrv_info, hotel_rsrv_code):
        try:
            user_id = User.query.filter_by(username=username).first().id

            trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
            if trip is None:
                raise Exception("No trip found")

            trip_flight = TripFlight.query.filter_by(trip_id=trip_id).first()
            trip.hotel_rsrv_code = hotel_rsrv_code if hotel_rsrv_code is not None and hotel_rsrv_code != '' else trip.hotel_rsrv
            if trip.hotel_rsrv_code is not None and trip.hotel_rsrv_code != '':
                trip.hotel_rsrv_code = "'" + trip.hotel_rsrv_code + "'"
            if flight_rsrv_info is not None and flight_rsrv_info != {}:
                trip_flight = flight_rsrv_info

            is_booked = False if trip_flight is None or trip_flight == {} or trip.hotel_rsrv_code is None else True

            self._upsert_trip_flight(trip_id, flight_rsrv_info)
            params = [trip_id, trip.hotel_rsrv_code, is_booked]
            self._exec_procedure(TRIP_UPDATE_RSRV_SP, params)
            self.db.session.commit()

            return_trip = self._get_trip(trip_id)
            return return_trip, 200
        except Exception as e:
            print(e)
            self.db.session.rollback()
            return "Error updating trip", 500

    def _get_string_param(self, param):
        return "'" + str(param) + "'"

    def _upsert_trip_flight(self, trip_id, flight):
        if flight is not None and flight != {}:
            arrival_time = self._get_string_param(flight['arrival_time'])
            departure_time = self._get_string_param(flight['departure_time'])
            from_city = City.query.filter_by(name=flight['from_city']).first().id
            to_city = City.query.filter_by(name=flight['to_city']).first().id
            duration = self._get_string_param(flight['duration'])
            price = flight['price']
            reservation_number = self._get_string_param(flight['reservation_number'])

            params = [trip_id, arrival_time, departure_time, from_city, to_city, duration, price, reservation_number]
            self._exec_procedure(UPSERT_TRIP_FLIGHT_SP, params)
            self.db.session.commit()

    def set_profile_attraction_rate(self, username, profile_id, attraction_id, rate):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, id=profile_id).first().id

            rate = int(rate)
            if rate < 1 or rate > 5:
                raise Exception("Rate is out of range")

            self._exec_procedure(PROFILE_RATE_SET_SP, [str(profile_id), str(attraction_id), str(rate)])
        except Exception as e:
            print(e)
            self.db.session.rollback()
            return "Error adding profile rate", 500
        return "success", 200

    #  GET FUNCTIONS

    def get_profile(self, username):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profiles = UserProfile.query.filter_by(user_id=user_id).with_entities(UserProfile.id, UserProfile.name).all()
            return jsonify({
                        'profiles': [{'id': profile.id, 'name': profile.name} for profile in profiles]
                   }), 200
        except Exception as e:
            return f"Error getting user's profiles: {str(e)}", 500

    def get_cities(self):
        try:
            return self.serialize_result(City.query.all()), 200
        except Exception as e:
            return f'Error getting cities: {str(e)}', 500

    def get_tags(self):
        try:
            return self.serialize_result(Tag.query.all())
        except Exception as e:
            return str(e), 500

    def get_attractions(self, **kwargs):
        if kwargs:
            if 'name' in kwargs:
                try:
                    attraction = Attraction.query.filter_by(name=kwargs['name']).first()
                    return attraction
                except:
                    return None
        try:
            return self.serialize_result(Attraction.query.all()), 200
        except Exception as e:
            return f"Error getting attractions: {str(e)}", 500

    def add_to_attr_tags(self, att_id, tag_id):
        try:
            tag_att = TagAttraction(tag_id=tag_id, attraction_id=att_id)
            self.db.session.add(tag_att)
            self.db.session.commit()
            return tag_att, 200
        except Exception as e:
            self.db.session.rollback()
            return f"Error adding tag to attractions: {str(e)}", 500

    def get_trip_attraction(self, trip_id, hotel, city_name):
        attractions_trip = TripAttraction.query.filter_by(trip_id=trip_id)
        parsed_attractions = []
        day = -1
        parsed_hotel = {
            'id': -1,
            'name': hotel['name'],
            'rate': 5,
            'address': hotel['address'],
            'price': hotel['price_per_night'],
            'description': '',
            'phone number': '',
            'website': hotel['url'],
            'city': city_name,
            'photo_url': hotel['main_photo_url'],
            'suggested_duration': ''
        }
        for attraction_trip in attractions_trip:
            attraction = Attraction.query.get(attraction_trip.attraction_id)
            parsed_attraction = {
                'id': attraction.id,
                'name': attraction.name,
                'rate': attraction.rate,
                'address': attraction.address,
                'price': attraction.price,
                'description': attraction.description,
                'phone number': attraction.phone_number,
                'website': attraction.website,
                'city': City.query.get(attraction.city_id).name,
                'photo_url': attraction.photo_url,
                'suggested_duration': attraction.suggested_duration
            }
            if (attraction_trip.day - 1) is not day:
                parsed_attractions.append([parsed_hotel])
                day += 1
            parsed_attractions[day].append(parsed_attraction)
        return parsed_attractions

    def get_trip_hotel(self, trip_id):
        trip_hotel = TripHotel.query.filter_by(trip_id=trip_id).first()
        if trip_hotel is None:
            return None
        hotel_data = Hotel.query.filter_by(id=trip_hotel.hotel_id).first()
        if hotel_data is None:
            return None
        hotel = {
            "address": hotel_data.address,
            "currency": trip_hotel.currency,
            "end_date": trip_hotel.end_date,
            "facilities": [],
            "main_photo_url": hotel_data.main_photo_url,
            "name": hotel_data.name,
            "price_per_night": trip_hotel.price_per_night,
            "room_type": trip_hotel.room_type,
            "start_date": trip_hotel.start_date,
            "url": hotel_data.url,
            "description": hotel_data.description,
            "stars": hotel_data.stars
        }
        return hotel

    def _get_trip_flight(self, trip_id):
        trip_flight = TripFlight.query.filter_by(trip_id=trip_id).first()
        if trip_flight is None:
            return {}

        from_city_name = City.query.get(trip_flight.from_city).name
        to_city_name = City.query.get(trip_flight.to_city).name

        flight = {
            "arrival_time": trip_flight.arrival_time,
            "departure_time": trip_flight.departure_time,
            "from_city": from_city_name,
            "from_city_code": LocationMatcher.get_iata_for_city(from_city_name),
            "to_city": to_city_name,
            "to_city_code":  LocationMatcher.get_iata_for_city(to_city_name),
            "duration": trip_flight.duration,
            "price": trip_flight.price,
            "reservation_number": trip_flight.reservation_number
        }
        return flight

    def _get_trip(self, trip_id):
        try:
            trip = Trip.query.filter_by(id=trip_id).first()
            city_name = City.query.get(trip.city_id).name

            hotel = self.get_trip_hotel(trip.id)
            flight = self._get_trip_flight(trip.id)
            attractions = self.get_trip_attraction(trip.id, hotel, city_name)
            if flight is not None and flight != {} and hotel is not None:
                trip.price = int(flight['price']) + (int(hotel['price_per_night'])*(trip.days-1))

            parsed_trip = {
                'id': trip.id,
                'profile': trip.profile_id,
                'destination': city_name,
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'days': trip.days,
                'price': trip.price,
                'currency': trip.currency,
                'people_number': int(trip.people_number),
                'pictures': [],
                'flights': [],
                'hotel': hotel,
                'explore': False,
                'places': attractions,
                'flight_rsrv': flight,
                'hotel_rsrv_code': trip.hotel_rsrv_code,
                'is_booked': trip.is_booked
            }
        except Exception as e:
            print(e)
            return str(e)
        else:
            return jsonify(parsed_trip)

    def get_trips(self, username):
        try:
            user_id = User.query.filter_by(username=username).first().id
            trips = Trip.query.filter_by(user_id=user_id)
            all_trips = []
            for trip in trips:
                city_name = City.query.get(trip.city_id).name
                flight = self._get_trip_flight(trip.id)
                hotel = self.get_trip_hotel(trip.id)
                if hotel is None:
                    continue
                attractions = self.get_trip_attraction(trip.id, hotel, city_name)

                if flight is not None and flight != {} and hotel is not None:
                    trip.price = int(flight['price']) + (int(hotel['price_per_night']) * (trip.days - 1))

                parsed_trip = {
                    'id': trip.id,
                    'profile': trip.profile_id,
                    'destination': city_name,
                    'start_date': trip.start_date,
                    'end_date': trip.end_date,
                    'days': trip.days,
                    'price': trip.price,
                    'currency': trip.currency,
                    'people_number': int(trip.people_number),
                    'pictures': [],
                    'flights': [],
                    'hotel': hotel,
                    'explore': False,
                    'places': attractions,
                    'flight_rsrv': flight,
                    'hotel_rsrv_code': trip.hotel_rsrv_code,
                    'is_booked': trip.is_booked
                }
                all_trips.append(parsed_trip)
        except Exception as e:
            return str(e), 500
        else:
            return jsonify(all_trips), 200

    def get_explore_trips(self, username, profile, from_date, to_date, city=None, travelers='2', budget =None):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, id=profile).first().id
            city_id = None
            if city:
                city_id = City.query.filter_by(name=city).first().id
            if budget:
                budget = int(budget)
            agent_response = requests.get(url=(AGENT_ENDPOINT+AGENT_ATTRACTION_GET), params={'profile_id': profile_id, 'city_id': city_id})
            fromdate = datetime.strptime(from_date, '%d/%m/%Y')
            todate = datetime.strptime(to_date, '%d/%m/%Y')
            days = (todate - fromdate).days
            estimated_requiired_attractions = days * 8

            if agent_response.status_code is not 200:
                return agent_response.content, agent_response.status_code
            agent_results = json.loads(agent_response.content)

            trips = []
            for result in agent_results:
                attractions = []
                city = City.query.filter_by(id=result['city_id']).first().name

                flight_price = 0
                flights = self._get_flights('tel aviv', city, from_date, to_date, travelers)
                if flights is not None and len(flights) > 0 and flights[1] is not 502:
                    flight_price = int(flights[0]["price"])
                else:
                    continue

                hotels = self._get_hotels(city, from_date, to_date, travelers)
                if hotels is None or len(hotels) == 0:
                    continue

                if '5' in result['attractions']:
                    attractions = result['attractions']['5']
                if '4'in result['attractions'] and len(attractions) <= estimated_requiired_attractions:
                    attractions.extend(result['attractions']['4'])
                if '3'in result['attractions'] and len(attractions) <= estimated_requiired_attractions:
                    attractions.extend(result['attractions']['3'])
                if '2'in result['attractions'] and len(attractions) <= estimated_requiired_attractions:
                    attractions.extend(result['attractions']['2'])
                if '1'in result['attractions'] and len(attractions) <= estimated_requiired_attractions:
                    attractions.extend(result['attractions']['1'])
                if len(attractions) < estimated_requiired_attractions*0.8:
                    continue

                trip_builder = CityWalkTripBuilder(DFSRoutesBuilder())
                attractions = [Attraction.query.get(attraction_id) for attraction_id in attractions]
                for hotel in hotels:
                    price = int(flight_price) + (int(hotel["price_per_night"])*days) #need to convert currencies
                    if budget is not None and price > budget:
                        continue

                    trips.append({
                        'id': -1,
                        'profile': profile_id,
                        'destination': city,
                        'start_date': from_date,
                        'end_date': to_date,
                        'days': days,
                        'price': price,
                        'currency': 'USD',
                        'people_number': travelers,
                        'pictures': [],
                        'flights': flights,
                        'hotel': hotel,
                        'explore': True,
                        'places': trip_builder.build_trip(days, attractions, city, hotel),
                        'flight_rsrv': None,
                        'hotel_rsrv_code': None,
                        'is_booked': False
                    })
            return jsonify(trips), 200
        except Exception as e:
            return str(e), 500

    def get_trip_config(self, city, username, profile):
        user_id = User.query.filter_by(username=username).first().id
        profile_id = UserProfile.query.filter_by(user_id=user_id, id=profile).first().id
        city_id = City.query.filter_by(name=city).first().id
        return {
            'user_id': user_id,
            'profile_id': profile_id,
            'city_id': city_id
        }

    def get_popular_tags(self):
        try:
            agent_response = requests.get(url=(AGENT_ENDPOINT+AGENT_TAGS_GET), params={})
            if agent_response.status_code is not 200:
                return agent_response.content, agent_response.status_code
            agent_results = json.loads(agent_response.content)
            tags = []
            for result in agent_results:
                id = result[0]
                tag = result[1]
                tags.append(
                    {"id": id, "name": tag}
                )
            return jsonify(tags), 200
        except Exception as e:
            return str(e), 500

    def _get_flights(self, from_city, to_city, from_date, to_date, travelers, max_stop_overs=3):
        max_returned_values = 3
        from_city_code = LocationMatcher.get_iata_for_city(from_city)
        to_city_code = LocationMatcher.get_iata_for_city(to_city)

        for stops in range(0, max_stop_overs):
            flight_url = FLIGHTS_BASE_ENDPOINT + 'flyFrom=' + from_city_code + '&to=' + to_city_code + '&dateFrom=' \
                         + from_date + '&dateTo=' + to_date + '&partner=picky&flight_type=return&' \
                         + 'max_stopovers=' + str(stops)
            api_response = requests.get(url=flight_url, params={})
            if api_response.status_code is not 200:
                return api_response.content, api_response.status_code
            api_results = json.loads(api_response.content)
            if len(api_results['data']) == 0:
                continue

            flights = []
            max_returned_values = min(max_returned_values, len(api_results['data']))
            for i in range(max_returned_values):
                flights.append(
                    {
                        "from_city": from_city,
                        "from_city_code": from_city_code,
                        "to_city": to_city,
                        "to_city_code": to_city_code,
                        "arrival_time": self._get_time_from_timestamp(api_results['data'][i]['aTime']),
                        "departure_time": self._get_time_from_timestamp(api_results['data'][i]['dTime']),
                        "price": api_results['data'][i]['price'],
                        "duration": api_results['data'][i]['fly_duration'],
                        "link": api_results['data'][i]['deep_link']
                    }
                )
            return flights

    def get_flights_for_trip(self, from_city, to_city, from_date, to_date, travelers, max_stop_overs=0):
        try:
            flights = self._get_flights(from_city, to_city, from_date, to_date, travelers, max_stop_overs)
            return jsonify(flights), 200
        except Exception as e:
            return str(e), 500

    def _get_hotels(self, city_name, from_date, to_date, travelers, rooms='1'):
        max_returned_values = 2

        city_code = LocationMatcher.get_booking_code_for_city(city_name)
        from_date = datetime.strptime(from_date, '%d/%m/%Y')
        to_date = datetime.strptime(to_date, '%d/%m/%Y')
        days = (to_date - from_date).days

        search_url = HOTELS_BASE_ENDPOINT + 'dest_ids=' + city_code + '&arrival_date=' \
                     + str(from_date.date()) + '&departure_date=' + str(to_date.date()) + '&guest_qty=' + str(travelers) \
                     + '&room_qty=' + rooms

        api_response = requests.get(url=search_url, headers=HOTELS_HEADER)
        if api_response.status_code is not 200:
            return api_response.content, api_response.status_code
        api_results = json.loads(api_response.content)
        hotels = []
        api_results_data = api_results['result']
        max_returned_values = min(max_returned_values, len(api_results_data))

        for i in range(max_returned_values):
            if 'price_breakdown' not in api_results_data[i].keys():
                continue
            row_data = api_results_data[i]
            address = str(row_data['address_trans']) + ',' + str(row_data['district']) + ',' + \
                      str(row_data['city_trans']) + ',' + str(row_data['zip']) + ',' + \
                      str(row_data['country_trans'])
            stars = str(row_data['class']) if row_data['class']!=0 else 'Not Specified'

            hotels.append(
                {
                    "address": address,
                    "currency": row_data['price_breakdown']['currency'],
                    "end_date": to_date.date(),
                    "facilities": [],
                    "main_photo_url": row_data['main_photo_url'].replace('square60', 'square350'),
                    "name": row_data['hotel_name'],
                    "price_per_night": (float(row_data['price_breakdown']['gross_price']) / days),
                    "room_type": "",
                    "start_date": from_date.date(),
                    "url": row_data['url'],
                    "description": '',
                    "stars": stars
                }
            )
        return hotels

    def get_hotels(self, city_name, from_date, to_date, travelers, rooms='1'):
        try:
            hotels = self._get_hotels(city_name, from_date, to_date, travelers, rooms)
            return jsonify(hotels), 200
        except Exception as e:
            return str(e), 500

    #Delete functions

    def delete_profile(self, username, profile_id):
        try:
            user = User.query.filter_by(username=username).first()
            profile_id = UserProfile.query.filter_by(user_id=user.id, id=profile_id).first().id
            self._exec_procedure(PROFILE_REMOVE_SP, [str(profile_id)])
        except Exception as e:
            print(e)
            return "Error removing a profile", 500
        return "success", 200

    #Private functions

    def _get_time_from_timestamp(self,timestamp):
        dt = datetime.utcfromtimestamp(int(timestamp)).strftime('%H:%M')
        return dt

    def _exec_procedure(self, procedure_name, params):
        try:
            params_conc = self._join(params, ',')
            print(params_conc)
            query = 'CALL ' + procedure_name + "(" + params_conc + ")"
            results = self.db.session.execute(query, [])
            self.db.session.commit()
            return results
        except Exception as e:
            self.db.session.rollback()
            print(e)
            raise e

    def _join(self, l, sep):
        out_str = ''
        for el in l:
            if el is None:
                el = 'Null'
            out_str += '{}{}'.format(el, sep)
        return out_str[:-len(sep)]

