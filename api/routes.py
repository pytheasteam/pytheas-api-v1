from flask import request, make_response, json
from flask import current_app as app
from .db_manager import DBManager

db_manager = DBManager()


@app.route('/login', methods=['POST'])
def entry():
    body = json.loads(request.data)
    response = db_manager.create_user(
        username=body.get('username'),
        email=body.get('email'),
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


@app.route('/migrate_data', methods=['POST'])
def migrate_data():
    resp = db_manager.migrate_data()
    return make_response(resp)