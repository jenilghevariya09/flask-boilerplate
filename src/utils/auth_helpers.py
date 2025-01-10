from flask_jwt_extended import decode_token, get_jwt_identity, JWTManager, create_access_token
from flask import current_app, jsonify
import datetime

def decode_auth_token(auth_token):
    try:
        # Decode the auth token to get the identity
        payload = decode_token(auth_token)
        return payload["identity"]
    except Exception as e:
        return None

def create_jwt_token(identity):
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=identity, expires_delta=expires)
    return access_token

def is_token_expired(token):
    try:
        payload = decode_token(token)
        exp_timestamp = payload["exp"]
        exp_date = datetime.datetime.utcfromtimestamp(exp_timestamp)
        return exp_date < datetime.datetime.utcnow()
    except Exception as e:
        return True
