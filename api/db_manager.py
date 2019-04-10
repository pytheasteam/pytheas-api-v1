from datetime import datetime as dt

from flask import jsonify

from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.user import User
from . import db


class DBManager:

    def create_user(self, username, email, google_token):
        try:
            session_token = ""
            new_user = User(
                username=username,
                email=email,
                created=dt.now(),
                google_token=google_token,
                session_token=session_token
            )
            db.session.add(new_user)
            db.session.commit()
            return session_token, 200
        except:
            return "Error", 500

    def create_tag(self, tag_name):
        try:
            new_tag = Tag(
                name=tag_name
            )
            db.session.add(new_tag)
            db.session.commit()
            return new_tag, 200
        except:
            return "Error", 500

    def get_tags(self):
        try:
            tags = Tag.query.all()
            tag_list = [{
                'id': tag.id,
                'name': tag.name
            } for tag in tags]
            return jsonify(tag_list), 200
        except:
            return "Error", 500

    def create_attraction(self, name, rate, address, price, description, phone, website, city_id):

        try:
            new_attraction = Attraction(
                name,
                rate,
                address,
                price,
                description,
                phone,
                website,
                city_id
            )
            db.session.add(new_attraction)
            db.session.commit()
            return new_attraction, 200
        except:
            return "Error", 500

    def get_attractions(self):
        try:
            attractions = Attraction.query.all()
            attraction_list = [{
                'id': attraction.id,
                'name': attraction.name,
                'rate': attraction.rate,
                'address': attraction.address,
                'price': attraction.price,
                'description': attraction.description,
                'phone number': attraction.phone_number,
                'website': attraction.website,
                'city name': City.query.filter(id=attraction.city_id).name
            } for attraction in attractions]
            return jsonify(attraction_list), 200
        except:
            return "Error", 500
