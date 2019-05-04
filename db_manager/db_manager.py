from datetime import datetime as dt
from flask import jsonify
from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.tag_attraction import TagAttraction
from api.models.user import User
from api.models.user_trip_profile import UserProfile, ProfileTag
from db_manager.pytheas_db_manager_base import PytheasDBManagerBase


class SQLPytheasManager(PytheasDBManagerBase):

    def __init__(self, db):
        super().__init__(db)

    def init(self):
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
            print(e)
            return "Error creating new model", 500

    def create_user(self, username, full_name, email, google_token):
        response = self._create(
            User,
            username=username,
            full_name=full_name,
            created=dt.now(),
            email=email,
            google_token=google_token
        )
        if response[1] == 200:
            return "37879879878", 200
        return "Error Creating New User", 500

    def create_tag(self, tag_name):
        response = self._create(Tag, name=tag_name)
        if response[1] == 200:
            return str(response[0]), 200
        return "Error Creating New Tag", 500

    def create_attraction(self,
                          name,
                          rate,
                          address,
                          price,
                          description,
                          phone,
                          website,
                          city_id,
                          attraction_id=None):

        try:
            new_attraction = Attraction(
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
            self.db.session.add(new_attraction)
            self.db.session.commit()
            return new_attraction, 200
        except Exception as e:
            return e, 500

    def create_city(self, name, country, city_id=None):
        try:
            new_city = City(
                name=name,
                country=country,
                id=city_id
            )
            self.db.session.add(new_city)
            self.db.session.commit()
            return new_city, 200
        except:
            return "Error", 500

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
            return "Error", 500
        else:
            return "success", 200

    #  GET FUNCTIONS
    def get_cities(self):
        try:
            return self.serialize_result(City.query.all()), 200
        except:
            return 'Error', 500

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
        except:
            return "Error", 500

    def add_to_attr_tags(self, att_id, tag_id):
        try:
            tag_att = TagAttraction(tag_id=tag_id, attraction_id=att_id)
            self.db.session.add(tag_att)
            self.db.session.commit()
            return tag_att, 200
        except Exception as e:
            self.db.session.rollback()
            return "Error", 500

    def get_explore_trips(self, city, username, profile, days):
        try:
            user_id = User.query.filter_by(username=username).first().id
            profile_id = UserProfile.query.filter_by(user_id=user_id, name=profile).first().id
            city_id = City.query.filter_by(name=city).first().id
            tags_id = [tag.tag_id for tag in ProfileTag.query.filter_by(profile_id=profile_id)]
            attractions = Attraction.query.filter_by(city_id=city_id)
            chosen_attractions = []
            for attraction in attractions:
                try:
                    at_tag = TagAttraction.query.filter_by(attraction_id=attraction.id)
                except:
                    pass
                else:
                    try:
                        attraction_tags = [
                            tag.tag_id for tag in at_tag
                        ]
                        if list(set(tags_id) & set(attraction_tags)):
                            chosen_attractions.append({
                                'id': attraction.id,
                                'name': attraction.name,
                                'rate': attraction.rate,
                                'address': attraction.address,
                                'price': attraction.price,
                                'description': attraction.description,
                                'phone number': attraction.phone_number,
                                'website': attraction.website,
                                'city': City.query.get(attraction.city_id).name
                            })
                    except Exception as e:
                        print(e)

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
            return e, 500





