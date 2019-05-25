import jwt
from flask import request, make_response, json
from flask import current_app as app
from flask_cors import CORS
from db_manager.config.secrets import SERVER_SECRET_KEY

from db_manager.db_manager import SQLPytheasManager
from . import db

db_manager = SQLPytheasManager(db)

CORS(app, supports_credentials=True, resources={r'/*': {"origins": '*'}})


@app.route('/')
def index():
    return 'Server is running'


@app.route('/login', methods=['POST'])
def entry():
    try:
        body = json.loads(request.data)
        response = db_manager.create_user(
            username=body.get('email'),
            email=body.get('email'),
            full_name=body.get('full_name'),
            google_token=body.get('google_token')
        )
    except:
        response = 'Invalid request', 400
    return make_response(response)


@app.route('/api')
def api_index():
    db_manager.initialize()
    return 'api index'


@app.route('/api/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_tag(
            tag_name=body.get('name')
        )
        return make_response(response)
    response = db_manager.get_tags()
    return response


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


@app.route('/api/explore', methods=['GET'])
def explore():
    city = 'paris'
    token = request.headers.get('Authorization').split(' ')[1]
    username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])
    response = db_manager.get_explore_trips(
        city=city,
        username=username,
        profile='art',
        days=3
    )
    return make_response(response)


@app.route('/api/trip', methods=['GET', 'POST', 'PUT'])
def trip():
    response = 500
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_trip(
            username=body.get('username'),
            start_date=body.get('start_date'),
            end_date=body.get('end_date'),
            price=body.get('price'),
            flight=body.get('flight'),
            hotel=body.get('hotel'),
            explore_trip=body.get('trip')  # Same as the explore trip that sent in /api/explore
        )
    elif request.method == 'PUT':
        pass
    else:
        try:
            token = request.headers.get('Authorization').split(' ')[1]
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])
            # username = 'userTest'
        except Exception as e:
            return make_response(f'Cannot find token in headers: {e}', 400)
        else:
            response = db_manager.get_trips(username)

    return make_response(response)
