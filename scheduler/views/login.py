from flask import Blueprint
from flask import request
from flask import jsonify
from flask.globals import _app_ctx_stack
from scheduler.schema import schema
from scheduler.db import db_session
from scheduler.models import User
import requests
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)

login_bp = Blueprint('login', __name__) 

GOOGLE_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={0}'

def get_google_token(token_id):
    result = requests.get(GOOGLE_URL.format(token_id))
    if not result.ok or result.status_code != 200:
        app = Flask(__name__, instance_relative_config=True)
        app.logger.warning('unable to check google token.')
        return None
    return result.json()

@login_bp.route('/login', methods=(['POST']))
def login():
    auth_data = request.get_json()
    token_id = auth_data.get('tokenId')
    google_token = get_google_token(token_id)
    if 'error_description' in google_token:
        return jsonify({
            'message': 'Token is invalid: {0}'.format(google_token['error_description']),
            'type': 'error'
        })
    email = google_token.get('email')
    user = User.query.get(email)
    if not user:
        new_user = User(
            email=email,
            name=google_token.get('name'),
            surname=google_token.get('surname'),
            fullname=google_token.get('name'),
            avatar=google_token.get('picture'),
        )
        db_session.add(new_user)
        db_session.commit()
    
    access_token = create_access_token(identity = email)
    refresh_token = create_refresh_token(identity = email)
    return jsonify({
        'message': 'Logged in as {}'.format(google_token.get('name')),
        'access_token': access_token,
        'refresh_token': refresh_token
        })

@login_bp.route('/protected')
@jwt_required
def protected():
    return 'Logged in as: ' + get_jwt_identity()
