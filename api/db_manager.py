from datetime import datetime as dt
from errno import errorcode

import mysql.connector
from flask import jsonify
from config.db import migration_db
from api.models.attraction import Attraction
from api.models.city import City
from api.models.tag import Tag
from api.models.tag_attraction import TagAttraction
from api.models.user import User
from . import db


class DBManager:

    def create(self, model, **kwargs):
        try:
            new_model = model(**kwargs)
            db.session.add(new_model)
            db.session.commit()
            return new_model, 200
        except:
            return "Error", 500

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

    # def create_tag(self, tag_name, tag_id=None):
    #     try:
    #         new_tag = Tag(
    #             id=tag_id,
    #             name=tag_name
    #         )
    #         db.session.add(new_tag)
    #         db.session.commit()
    #         return new_tag, 200
    #     except:
    #         return "Error", 500

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

    # def create_attraction(self,
    #                       name,
    #                       rate,
    #                       address,
    #                       price,
    #                       description,
    #                       phone,
    #                       website,
    #                       city_id,
    #                       attraction_id=None):
    #
    #     try:
    #         new_attraction = Attraction(
    #             id=attraction_id,
    #             name=name,
    #             rate=rate,
    #             address=address,
    #             price=price,
    #             description=description,
    #             phone_number=phone,
    #             website=website,
    #             city_id=city_id
    #         )
    #         db.session.add(new_attraction)
    #         db.session.commit()
    #         return new_attraction, 200
    #     except Exception as e:
    #         return e, 500

    def get_attractions(self, **kwargs):
        if kwargs:
            if 'name' in kwargs:
                try:
                    attractions = Attraction.query.filter_by(name=kwargs['name']).first()
                    return attractions
                except:
                    return None
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

    # def create_city(self, name, country, city_id=None):
    #     try:
    #         new_city = City(
    #             name=name,
    #             country=country,
    #             id=city_id
    #         )
    #         db.session.add(new_city)
    #         db.session.commit()
    #         return new_city, 200
    #     except:
    #         return "Error", 500


    def add_to_attr_tags(self, att_id, tag_id):
        try:
            tag_att = TagAttraction(tag_id=tag_id, attraction_id=att_id)
            db.session.add(tag_att)
            db.session.commit()
            return tag_att, 200
        except Exception as e:
            db.session.rollback()
            return "Error", 500

    def migrate_data(self):
        try:
            db_client = mysql.connector.connect(
                host=migration_db.HOST,
                database=migration_db.DATABASE_NAME,
                user=migration_db.USERNAME,
                password=migration_db.PASSWORD
            )
            cursor = db_client.cursor()

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Bad username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            print("Migrate tag attr")
            x = TagAttraction.query.delete()
            print(f'delete {x} rows' )
            query = "SELECT * FROM pytheas.api_attraction_tags;"
            cursor.execute(query)
            res = cursor.fetchall()
            print(len(res))
            for attag in res:
                try:
                    print(attag)
                    self.add_to_attr_tags(attag[1], attag[2])
                except:
                    pass
        return '200'

