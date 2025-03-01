from flask import jsonify
from datetime import datetime, timezone
from models.user_model import User
from models.settings_model import Settings
from models.broker_credentials_model import BrokerCredentials
from models.token import Token
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP
from utils.get_broker import get_token

http = HTTP()

bcrypt = Bcrypt()

def register_user(cursor, data):
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        data['password'] = hashed_password
        data['status'] = 'trial'
        data['trialDate'] = datetime.now(timezone.utc)
        User.register_user(cursor, data)
        user = User.get_user_by_email(cursor, data['email'])
        if user:
            access_token = create_jwt_token(identity=user.get('email'))
            Settings.upsert_setting(cursor, {"userId": user.get('id'), "theme_mode" : 'light', "symbol": "NIFTY"})
            setting = Settings.get_setting_by_userId(cursor, user.get('id'))
        return jsonify({"access_token": access_token, "user_data": user, "setting": setting,}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while registering the user", "error": str(e)}), 500

def login_user(cursor, email, password):
    try:
        user_detail = User.find_by_email(cursor, email)
        if user_detail and bcrypt.check_password_hash(user_detail.get('password'), password):
            access_token = create_jwt_token(identity=email)
            user = User.get_user_by_email(cursor, email)
            planStatus = user.get('status')
            if planStatus == 'active' and user.get('expiryDate'):
                expiry_date = user['expiryDate']
                if expiry_date.tzinfo is None:
                    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                if expiry_date < datetime.now(timezone.utc):
                    updated_user = {
                        "planId": None,
                        "status": "expired",
                    }
                    User.update_profile(cursor, user.get('id'), updated_user)
                    user = User.get_user_by_id(cursor, user.get('id'))
            brokerType = None
            Settings.upsert_setting(cursor, {"userId": user.get('id'), "predefined_mtm_sl" : None, "predefined_mtm_target" : None})
            setting = Settings.get_setting_by_userId(cursor, user.get('id'))
            
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.get('id'))
            if brokercredentials and brokercredentials[0]:
                data = brokercredentials[0]
                brokerType = data.get('brokerServer')
                if brokerType == 'Upstox':
                    return jsonify({"access_token": access_token, "user_data": user, "broker_type": brokerType, "setting": setting, "brokercredentials": brokercredentials}), 200
                def check_error(response):
                    if response.get('isError'):
                        return jsonify(response), 400
                    return None
                token_response = get_token(cursor, data, user.get('id'))
                if (error := check_error(token_response)):
                    return error
                
                client_code = token_response.get('user_session').get('result', {}).get('clientCodes')
                if client_code and client_code[0]:
                    data['client_code'] = client_code[0]
                        
                token = Token.get_token_by_user(cursor, user.get('id'))
                    
            return jsonify({"access_token": access_token, "user_data": user, "setting": setting, "brokercredentials": brokercredentials, "token": token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500

def logout_user(cursor, email):
    try:
        user = User.get_user_by_email(cursor, email)
        if user:
            
            Settings.upsert_setting(cursor, {"userId": user.get('id'), "predefined_mtm_sl" : None, "predefined_mtm_target" : None})
            Token.delete_tokens(cursor, user.get('id'))
            
            return jsonify({"message": "User logged out successfully"}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred during logout", "error": str(e)}), 500
    
def preload_data(cursor, email):
    try:
        user = User.get_user_by_email(cursor, email)
        if user:
            planStatus = user.get('status')
            if planStatus == 'active' and user.get('expiryDate'):
                expiry_date = user['expiryDate']
                if expiry_date.tzinfo is None:
                    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                if expiry_date < datetime.now(timezone.utc):
                    updated_user = {
                        "planId": None,
                        "status": "expired",
                    }
                    User.update_profile(cursor, user.get('id'), updated_user)
                    user = User.get_user_by_id(cursor, user.get('id'))
            
            
            setting = Settings.get_setting_by_userId(cursor, user.get('id'))
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.get('id'))
            token = Token.get_token_by_user(cursor, user.get('id'))
                
            return jsonify({"user_data": user, "setting": setting, "brokercredentials": brokercredentials, "tokens": token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
