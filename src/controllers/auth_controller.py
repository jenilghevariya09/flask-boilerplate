from flask import jsonify
from models.user_model import User
from models.settings_model import Settings
from models.broker_credentials_model import BrokerCredentials
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP
from utils.callApi import call_host_lookup_api, call_user_session_api, call_user_market_api

http = HTTP()

bcrypt = Bcrypt()

def register_user(cursor, data):
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        data['password'] = hashed_password
        User.register_user(cursor, data)
        user = User.find_by_email(cursor, data['email'])
        formatted_setting = None
        if user:
            access_token = create_jwt_token(identity=user.email)
            user_data = {
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name ": user.first_name,
                "last_name ": user.last_name,
                "email": user.email
            }
            Settings.upsert_setting(cursor, {"userId": user.id})
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "close_order_type",
                    "predefined_sl", "sl_type", "is_trailing", "predefined_target",
                    "target_type", "predefined_mtm_sl", "mtm_sl_type", "predefined_mtm_target",
                    "mtm_target_type", "lot_multiplier", "userId"
                ]
                formatted_setting = format_single_query_result(setting, column_names)
        return jsonify({"access_token": access_token, "user_data": user_data, "setting": formatted_setting,}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while registering the user", "error": str(e)}), 500

def login_user(cursor, email, password):
    try:
        user = User.find_by_email(cursor, email)
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_jwt_token(identity=user.email)
            user_data = {
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name ": user.first_name,
                "last_name ": user.last_name,
                "email": user.email
            }
            formatted_setting = None;
            formatted_brokercredentials = None;
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "close_order_type",
                    "predefined_sl", "sl_type", "is_trailing", "predefined_target",
                    "target_type", "predefined_mtm_sl", "mtm_sl_type", "predefined_mtm_target",
                    "mtm_target_type", "lot_multiplier", "userId"
                ]
                formatted_setting = format_single_query_result(setting, column_names)
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.id)
            host_lookup_response = None
            user_market_response = None
            user_session_response = None
            if brokercredentials:
                column_names = [
                    "id", "brokerServer", "MarketApiKey", "MarketSecretKey", "InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId"
                ]
                formatted_brokercredentials = format_query_result(brokercredentials, column_names)
                
                if formatted_brokercredentials and formatted_brokercredentials[0]:
                    data = formatted_brokercredentials[0]
                    user_market_response = call_user_market_api(cursor, data, user_data.get('id'))
                    
                    host_lookup_response = call_host_lookup_api()
                    if not host_lookup_response.get('isError', False):
                        user_session_response = call_user_session_api(cursor, data, host_lookup_response, user_data.get('id'))
            return jsonify({"access_token": access_token, "user_data": user_data, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials, "user_market_response": user_market_response, "host_lookup": host_lookup_response, "Interactive_session" : user_session_response}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
