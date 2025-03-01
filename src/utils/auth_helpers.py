from flask_jwt_extended import decode_token, get_jwt_identity, JWTManager, create_access_token
from datetime import datetime, timezone, timedelta

def decode_auth_token(auth_token):
    try:
        # Decode the auth token to get the identity
        payload = decode_token(auth_token)
        return payload["identity"]
    except Exception as e:
        return None

def create_jwt_token(identity):
    now = datetime.now(timezone.utc)
    tomorrow_2am = now.replace(hour=2, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    # If the current time is after 2 AM, set the expiration to 2 AM the next day
    if now > tomorrow_2am:
        tomorrow_2am += timedelta(days=1)
    
    expires_delta = tomorrow_2am - now
    access_token = create_access_token(identity=identity, expires_delta=expires_delta)
    return access_token

def is_token_expired(token):
    try:
        payload = decode_token(token)
        exp_timestamp = payload["exp"]
        exp_date = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        return exp_date < datetime.now(timezone.utc)
    except Exception as e:
        return True
