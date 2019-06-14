import json
from datetime import datetime as dt, datetime

import requests
from flask import jsonify
import jwt

from db_manager.config.agent_url import AGENT_ENDPOINT, AGENT_ATTRACTION_GET, AGENT_TAGS_GET
from db_manager.config.secrets import SERVER_SECRET_KEY
from db_manager.config.exteranl_apis import FLIGHTS_BASE_ENDPOINT, HOTELS_BASE_ENDPOINT, HOTELS_HEADER
from db_manager.location_code_matcher import LocationMatcher
from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.tag_attraction import TagAttraction
from api.models.trip import Trip, TripAttraction
from api.models.user import User
from api.models.user_trip_profile import UserProfile, ProfileTag
from db_manager.pytheas_db_manager_base import PytheasDBManagerBase
from trip_builder.city_trip_builder import CityWalkTripBuilder
from trip_builder.routes_builder.basic_route_builder import BasicRoutesBuilder


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

    def create_trip(self, username, start_date, end_date, price, flight, hotel, explore_trip):
        try:
            user = User.query.filter_by(username=username).first()
            city = City.query.filter_by(name=explore_trip['destination']).first()
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            if flight is None and hotel is None:
                is_booked = False
            else:
                is_booked = True
            new_trip = Trip(
                user_id=user.id,
                start_date=start_date,
                end_date=end_date,
                price=price,
                is_booked=is_booked,
                city_id=city.id
            )
            self.db.session.add(new_trip)
            self.db.session.commit()
            for day in range(explore_trip['days']):
                for attraction in explore_trip['places'][day]:
                    new_trip_attraction = TripAttraction(
                        trip_id=new_trip.id,
                        attraction_id=attraction['id'],
                        day=day + 1
                    )
                    self.db.session.add(new_trip_attraction)
                    self.db.session.commit()
        except Exception as e:
            print(e)
            self.db.session.rollback()
            return "Error creating new profile", 500
        else:
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

    def get_trip_attraction(self, trip_id):
        attractions_trip = TripAttraction.query.filter_by(trip_id=trip_id)
        parsed_attractions = []
        day = -1
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
                'city': City.query.get(attraction.city_id).name
            }
            if (attraction_trip.day - 1) is not day:
                parsed_attractions.append([parsed_attraction])
                day += 1
            else:
                parsed_attractions[day].append(parsed_attraction)
        return parsed_attractions

    def get_trips(self, username):
        try:
            user_id = User.query.filter_by(username=username).first().id
            trips = Trip.query.filter_by(user_id=user_id)
            all_trips = []
            for trip in trips:
                parsed_trip = {
                        'start_date': trip.start_date,
                    'end_date': trip.end_date,
                    'price': trip.price,
                    'is_booked': bool(trip.is_booked),
                    'city': City.query.get(trip.city_id).name,
                    'flight': trip.flight_rsrv,
                    'hotel': trip.hotel_rsrv,
                    'places': self.get_trip_attraction(trip.id)
                }
                all_trips.append(parsed_trip)
        except Exception as e:
            return str(e), 500
        else:
            return jsonify(all_trips), 200

    def get_explore_trips(self, username, profile, from_date, to_date, city=None, travelers='2'):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, id=profile).first().id
            #profile_id = profile
            city_id = City.query.filter_by(name=city).first()
            city_id = city_id.id if city_id is not None else None
            agent_response = requests.get(url=(AGENT_ENDPOINT+AGENT_ATTRACTION_GET), params={'profile_id': profile_id, 'city_id': city_id})

            estimated_attractions_per_day = 8
            fromdate = datetime.strptime(from_date, '%d/%m/%Y')
            todate = datetime.strptime(to_date, '%d/%m/%Y')
            days = (todate - fromdate).days

            if agent_response.status_code is not 200:
                return agent_response.content, agent_response.status_code
            agent_results = json.loads(agent_response.content)

            trips = []
            for result in agent_results:
                attractions = []
                city = City.query.filter_by(id=result['city_id']).first().name

                flight_price = 0
                flights = self._get_flights('tel aviv', city, from_date, to_date, travelers)
                if flights is not None and len(flights) is not 0:
                    flight_price = int(flights[0]["price"])
                hotels = self._get_hotels(city, from_date, to_date, travelers)
                trip_builder = CityWalkTripBuilder(BasicRoutesBuilder())

                if '5' in result['attractions']:
                    attractions = result['attractions']['5']
                if '4'in result['attractions'] and len(attractions) <= (days*estimated_attractions_per_day):
                    attractions.extend(result['attractions']['4'])
                if '3'in result['attractions'] and len(attractions) <= (days*estimated_attractions_per_day):
                    attractions.extend(result['attractions']['3'])

                attractions = [Attraction.query.get(attraction_id) for attraction_id in attractions]
                for hotel in hotels:
                    price = int(flight_price) + (int(hotel["price_per_night"])*days) #need to convert currencies
                    trips.append({
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
                        'places': trip_builder.build_trip(days, attractions, city, hotel)
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


    def _get_flights(self, from_city, to_city, from_date, to_date, travelers, max_stop_overs=0):
        max_returned_values = 3
        from_city = LocationMatcher.get_iata_for_city(from_city)
        to_city = LocationMatcher.get_iata_for_city(to_city)
        flight_url = FLIGHTS_BASE_ENDPOINT + 'flyFrom=' + from_city + '&to=' + to_city + '&dateFrom=' \
                     + from_date + '&dateTo=' + to_date + '&partner=picky&flight_type=return&' \
                     + 'max_stopovers=0'
        api_response = requests.get(url=flight_url, params={})
        if api_response.status_code is not 200:
            return api_response.content, api_response.status_code
        api_results = json.loads(api_response.content)
        flights = []
        max_returned_values = min(max_returned_values, len(api_results['data']))
        for i in range(max_returned_values):
            flights.append(
                {
                    "duration": api_results['data'][i]['fly_duration'],
                    "air_line": api_results['data'][i]['airlines'][0],
                    "price": api_results['data'][i]['price'],
                    "departure_time": api_results['data'][i]['dTime'],
                    "arrival_time": api_results['data'][i]['aTime'],
                    "deep_ling": api_results['data'][i]['deep_link']
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
        max_returned_values = 3

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

            hotels.append(
                {
                    "name": row_data['hotel_name'],
                    "url": row_data['url'],
                    "start_date": from_date.date(),
                    "end_date": to_date.date(),
                    "room_type": "",
                    "price_per_night": (float(row_data['price_breakdown']['gross_price']) / days),
                    "currency": row_data['price_breakdown']['currency'],
                    "address": address,
                    "main_photo_url": row_data['main_photo_url'].replace('square60', 'square350'),
                    "facilities": []
                }
            )
        return hotels

    def get_hotels(self, city_name, from_date, to_date, travelers, rooms='1'):
        try:
            hotels = self._get_hotels(city_name, from_date, to_date, travelers, rooms)
            return jsonify(hotels), 200
        except Exception as e:
            return str(e), 500
