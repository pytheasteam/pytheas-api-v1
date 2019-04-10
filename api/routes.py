from flask import request, render_template, make_response, json, jsonify
from datetime import datetime as dt
from flask import current_app as app

from api.models.tag import Tag
from . import db
from .models.user import User


@app.route('/login', methods=['POST'])
def entry():
    """Endpoint to create a user."""
    new_user = User(username='userTest',
                    email='user.test@example.com',
                    created=dt.now(),
                    google_token='sdkjfhsdkjhfkjdshfks'
                    )
    db.session.add(new_user)
    db.session.commit()
    return make_response("User created!")


@app.route('/api/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'POST':
        body = json.loads(request.data)
        new_tag = Tag(
            name=body.get('name')
        )
        db.session.add(new_tag)
        db.session.commit()
        return make_response("Tag created!")
    tags = Tag.query.all()
    tag_list = [{
        'id': tag.id,
        'name': tag.name
    } for tag in tags]
    return make_response(jsonify(tag_list), 200)
