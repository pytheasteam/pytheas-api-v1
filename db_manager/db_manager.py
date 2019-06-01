import json
from datetime import datetime as dt, datetime

import requests
from flask import jsonify
import jwt

from agent.get_attractions_for_profile import agent_mock_call_stub
from db_manager.config.agent_url import AGENT_ENDPOINT
from db_manager.config.secrets import SERVER_SECRET_KEY
from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.tag_attraction import TagAttraction
from api.models.trip import Trip, TripAttraction
from api.models.user import User
from api.models.user_trip_profile import UserProfile, ProfileTag
from db_manager.pytheas_db_manager_base import PytheasDBManagerBase


class SQLPytheasManager(PytheasDBManagerBase):
    # TODO: Refactor exceptions handling
    # TODO: Replace DB to mys

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
        return jwt.encode({'username': username}, SERVER_SECRET_KEY, algorithm='HS256'), 200

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
            return jsonify({
                        'profiles': UserProfile.query.filter_by(user_id=user_id).with_entities(UserProfile.id, UserProfile.name).all()
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

    def get_explore_trips(self, username, profile, days, city=None, hotel=None):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, name=profile).first().id
            city_id = City.query.filter_by(name=city).first().id
            agent_response = requests.get(url=AGENT_ENDPOINT, params={'profile_id': profile_id, 'city_id': city_id})
            days = int(days)
            if agent_response.status_code is not 200:
                return agent_response.content, agent_response.status_code
            agent_results = json.loads(agent_response.content)
            # chosen_attractions = agent_mock_call_stub(profile_id, city_id)
            # TODO: Switch below section to trip builder strategy
            trips = []
            for result in agent_results:
                city = City.query.filter_by(id=result['city_id']).first().name
                attractions = result['attractions']['5']
                attractions.extend(result['attractions']['4'])
                chosen_attractions_by_days = []
                for day in range(0, days):
                    chosen_attractions_by_days.append([])
                for i, attraction in enumerate(attractions):
                    attraction_object = Attraction.query.filter_by(id=attraction).first()
                    chosen_attractions_by_days[i % days].append(
                        {
                            'id': attraction_object.id,
                            'name': attraction_object.name,
                            'rate': attraction_object.rate,
                            'address': attraction_object.address,
                            'price': attraction_object.price,
                            'description': attraction_object.description,
                            'phone number': attraction_object.phone_number,
                            'website': attraction_object.website,
                            'city': City.query.get(attraction_object.city_id).name
                        }
                    )
                trips = [{
                    'destination': city,
                    'days': days,
                    'places': chosen_attractions_by_days,
                    'number_of_places': len(attractions)
                }]
            return jsonify(trips), 200
        except Exception as e:
            return str(e), 500

    def get_trip_config(self, city, username, profile):
        user_id = User.query.filter_by(username=username).first().id
        profile_id = UserProfile.query.filter_by(user_id=user_id, name=profile).first().id
        city_id = City.query.filter_by(name=city).first().id
        return {
            'user_id': user_id,
            'profile_id': profile_id,
            'city_id': city_id
        }
