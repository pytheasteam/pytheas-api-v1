from flask import request, make_response, json
from flask import current_app as app
from flask_cors import CORS
from . import db

from .db_manager import PytheasDBManager

db_manager = PytheasDBManager(db)
CORS(app, supports_credentials=True)


@app.route('/')
def index():
    return 'hello'


@app.route('/api')
def api_index():
    return 'api index'


@app.route('/login', methods=['POST'])
def entry():
    body = json.loads(request.data)
    response = db_manager.create_user(
        username=body.get('username'),
        email=body.get('email'),
        full_name=body.get('full_name'),
        google_token=body.get('google_token')
    )
    return make_response(response)


@app.route('/api/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_tag(
            tag_name=body.get('name')
        )
        return make_response(response)
    response = db_manager.get_tags()
    return make_response(response)


@app.route('/api/cities', methods=['GET'])
def cities():
    response = db_manager.get_cities()
    return make_response(response)


@app.route('/api/attractions', methods=['GET', 'POST'])
def attractions():
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_attraction(
            name=body.get('name'),
            rate=body.get('rate'),
            address=body.get('address'),
            price=body.get('price', None),
            description=body.get('description', None),
            phone=body.get('phone_number', None),
            website=body.get('website', None),
            city_id=body.get('city_id')
        )
        return make_response(response)
    response = db_manager.get_attractions()
    return make_response(response)


@app.route('/api/profile', methods=['POST', 'GET'])
def profiles():
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_profile(
            username=body.get('username'),
            profile_name=body.get('name'),
            tags=body.get('tags')
        )
        return make_response(response)
    response = db_manager.get_attractions()
    return make_response(response)


@app.route('/api/explore', methods=['get'])
def explore():
    city = 'paris'
    response = db_manager.get_explore_trips(
        city=city,
        username='userTest',
        profile='art',
        days=3
    )
    return make_response(response)
