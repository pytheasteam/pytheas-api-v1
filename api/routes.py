import jwt
from flask import request, make_response, json, Response
from flask import current_app as app
from flask_cors import CORS, cross_origin
from db_manager.config.secrets import SERVER_SECRET_KEY

from db_manager.db_manager import SQLPytheasManager
from . import db

db_manager = SQLPytheasManager(db)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
@cross_origin()
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
@cross_origin()
def api_index():
    #  TODO: Replace with swagger
    db_manager.initialize()
    return 'api index'


@app.route('/api/tags', methods=['GET', 'POST'])
@cross_origin()
def tags():
    if request.method == 'POST':
        body = json.loads(request.data)
        response = db_manager.create_tag(
            tag_name=body.get('name')
        )
        return make_response(response)
    response = db_manager.get_popular_tags()
    return response


@app.route('/api/cities', methods=['GET'])
@cross_origin()
def cities():
    response = db_manager.get_cities()
    return make_response(response)


@app.route('/api/attractions', methods=['GET', 'POST'])
@cross_origin()
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
@cross_origin()
def profiles(profile_id=None):
    response = ''
    if request.method != 'GET':
        try:
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256']).get('username')
        except Exception as e:
            return make_response('Unauthorized', 401)

        if request.method == 'POST':
            body = json.loads(request.data)
            response = db_manager.create_profile(
                username=username,
                profile_name=body.get('name'),
                tags=body.get('tags')
            )
        if request.method == 'DELETE':
            response = db_manager.delete_profile(
                username=username,
                profile_id=profile_id,
            )
        return make_response(response)

    #  GET Method Implementation
    try:
        token = request.headers.get('Authorization')
        username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256']).get('username')
    except Exception as e:
        return make_response('Unauthorized', 401)
    response = db_manager.get_profile(username)
    return make_response(response)


@app.route('/api/explore', methods=['GET'])
@cross_origin()
def explore():
    city = request.args.get('city')
    profile = request.args.get('profile')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    travelers = request.args.get('travelers', 1)
    budget = request.args.get('price', None)
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
        travelers=travelers,
        budget=budget
    )
    return make_response(response)


@app.route('/api/explore_flight', methods=['GET'])
@cross_origin()
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
@cross_origin()
def explore_hotels():
    city_name = request.args.get('city')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    travelers = request.args.get('travelers', '1')
    rooms = request.args.get('rooms', '1')

    response = db_manager.get_hotels(city_name, from_date, to_date, travelers, rooms)
    return response


@app.route('/api/trip', methods=['GET', 'POST', 'PUT'])
@app.route('/api/trip/<trip_id>', methods=['DELETE'])
@cross_origin()
def trip(trip_id=None):
    response = 500
    if request.method == 'GET':
        try:
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
        except Exception as e:
            return make_response(f'Cannot find token in headers: {e}', 400)
        else:
            response = db_manager.get_trips(username)
    elif request.method == 'DELETE':
        try:
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
        except:
            return make_response('Unauthorized', 401)
        else:

            response = db_manager.delete_trip(username=username, trip_id=trip_id)
    else: #Post/ Put
        try:
            token = request.headers.get('Authorization')
            username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
        except:
            return make_response('Unauthorized', 401)

        body = json.loads(request.data)
        trip_data = {
            'id': int(body.get('id', -1)),
            'destination': body.get('destination'),
            'start_date': body.get('start_date'),
            'end_date': body.get('end_date'),
            'days': int(body.get('days')),
            'price': int(body.get('price')),
            'currency': body.get('currency'),
            'people_number': int(body.get('people_number')),
            'pictures': [],
            'hotel': body.get('hotel'),
            'places': body.get('places')
        }

        if request.method == 'POST':
            response = db_manager.create_trip(
                username=username,
                profile_id=body.get('profile'),
                flight_rsrv=body.get('flight_rsrv', None),
                hotel_rsrv_code=body.get('hotel_rsrv_code', None),
                trip_data=trip_data
            )
        elif request.method == 'PUT':
            response = db_manager.upsert_trip(
                username=username,
                profile_id=body.get('profile'),
                flight_rsrv=body.get('flight_rsrv', None),
                hotel_rsrv_code=body.get('hotel_rsrv_code', None),
                trip_data=trip_data
            )
    return make_response(response)


@app.route('/api/profile_attraction', methods=['POST'])
@cross_origin()
def profile_attraction():
    body = json.loads(request.data)
    profile = body.get('profile')
    attraction = body.get('attraction')
    rate = body.get('rate')

    try:
        token = request.headers.get('Authorization')
        username = jwt.decode(token, SERVER_SECRET_KEY, algorithms=['HS256'])['username']
    except:
        return make_response('Unauthorized', 401)

    response = db_manager.set_profile_attraction_rate(
        username=username,
        profile_id=profile,
        attraction_id=attraction,
        rate=rate
    )
    return make_response(response)
