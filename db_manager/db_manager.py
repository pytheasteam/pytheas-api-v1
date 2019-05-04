from datetime import datetime as dt, datetime
from flask import jsonify

from agent.get_attractions_for_profile import agent_mock_call_stub
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
            new_model = model(*kwargs)
            self.db.session.add(new_model)
            self.db.session.commit()
            return new_model, 200
        except Exception as e:
            return f"Error creating {model}: {e}", 500

    def create_user(self, username, full_name, email, google_token):
        return self._create(
            User,
            username=username,
            full_name=full_name,
            created=dt.now(),
            email=email,
            google_token=google_token
        )

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

    def create_trip(self, username, start_date, end_date, price, is_booked, explore_trip):
        try:
            user = User.query.filter_by(username=username).first()
            city = City.query.filter_by(name=explore_trip['destination']).first()
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
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
                        day=day+1
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

    def get_explore_trips(self, city, username, profile, days):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, name=profile).first().id
            city_id = City.query.filter_by(name=city).first().id
            # TODO: Call the agent for getting the attractions
            chosen_attractions = agent_mock_call_stub(profile_id, city_id)
            # TODO: Switch below section to trip builder strategy
            chosen_attractions_by_days = []
            for day in range(0, days):
                chosen_attractions_by_days.append([])
            for i, attraction in enumerate(chosen_attractions):
                chosen_attractions_by_days[i % days].append(attraction)
            trips = [{
                'destination': city,
                'days': days,
                'places': chosen_attractions_by_days,
                'number_of_places': len(chosen_attractions)
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

