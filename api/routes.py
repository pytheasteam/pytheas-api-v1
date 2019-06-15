import jwt
from flask import request, make_response, json
from flask import current_app as app
from flask_cors import CORS, cross_origin
from db_manager.config.secrets import SERVER_SECRET_KEY

from db_manager.db_manager import SQLPytheasManager
from . import db

db_manager = SQLPytheasManager(db)

CORS(app, supports_credentials=True, resources={r'/*': {"origins": '*', "headers": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return 'Server is running'


@app.route('/login', methods=['POST'])
@cross_origin()
def entry():
    try:
        body = json.loads(request.data)
        response = db_manager.create_user(
            username=body.get('email'),
            email=body.get('email'),
            full_name=body.get('full_name'),
            google_token=body.get('google_token')
        )
    except Exception as e:
        response = 'Invalid request', 400
    return make_response(response)


@app.route('/api')
def api_index():
    #  TODO: Replace with swagger
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
    #response = db_manager.get_tags()
    response = db_manager.get_popular_tags()
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
@app.route('/api/profile/<profile_id>', methods=['DELETE'])
def profiles(profile_id=None):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256']).get('username')
        except Exception as e:
            return make_response('Unauthorized', 401)
        body = json.loads(request.data)
        response = db_manager.create_profile(
            username=username,
            profile_name=body.get('name'),
            tags=body.get('tags')
        )
        return make_response(response)
    if request.method == 'DELETE':
        print(profile_id) # The profile we want to delete
        # PUT your logics here or call to db_manager function
        return make_response("LACHMI THE KING", 200)

    #  GET Method Implementation
    try:
        token = request.headers.get('Authorization')
        username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256']).get('username')
    except Exception as e:
        return make_response('Unauthorized', 401)
    response = db_manager.get_profile(username)
    return make_response(response)


@app.route('/api/explore', methods=['GET'])
def explore():
    city = request.args.get('city')
    profile = request.args.get('profile')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    travelers = request.args.get('travelers', 1)

    try:
        token = request.headers.get('Authorization')
        username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
    except:
        return make_response('Unauthorized', 401)

    response = db_manager.get_explore_trips(
        city=city,
        username=username,
        profile=profile,
        from_date=from_date,
        to_date=to_date,
        travelers=travelers
    )
    return make_response(response)


@app.route('/api/explore_flight', methods=['GET'])
def explore_flight():
    from_city = request.args.get('from_city', 'tel aviv')
    to_city = request.args.get('to_city')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    travelers = request.args.get('travelers', 1)
    max_stop_overs = request.args.get('stopovers', 0)

    response = db_manager.get_flights_for_trip(from_city, to_city, from_date, to_date, travelers, max_stop_overs)
    return response


@app.route('/api/explore_hotels', methods=['GET'])
def explore_hotels():
    city_name = request.args.get('city')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    travelers = request.args.get('travelers', '1')
    rooms = request.args.get('rooms', '1')

    response = db_manager.get_hotels(city_name, from_date, to_date, travelers, rooms)
    return response


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
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
        except Exception as e:
            return make_response(f'Cannot find token in headers: {e}', 400)
        else:
            response = db_manager.get_trips(username)

    return make_response(response)
