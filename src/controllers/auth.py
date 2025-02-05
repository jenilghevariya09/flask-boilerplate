from flask import jsonify
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
        User.register_user(cursor, data)
        user = User.find_by_email(cursor, data['email'])
        formatted_setting = None
        if user:
            access_token = create_jwt_token(identity=user.email)
            user_data = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "country": user.country,
                "state": user.state,
                "city": user.city,
            }
            Settings.upsert_setting(cursor, {"userId": user.id, "theme_mode" : 'light'})
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "limit_price",
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
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "country": user.country,
                "state": user.state,
                "city": user.city,
            }
            formatted_setting = None
            formatted_brokercredentials = None
            formatted_token = None
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "limit_price",
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
                    "id", "brokerServer", "MarketApiKey", "MarketSecretKey", "InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId", "interactiveUserId", "marketUserId", "client_code"
                ]
                formatted_brokercredentials = format_query_result(brokercredentials, column_names)
                
                if formatted_brokercredentials and formatted_brokercredentials[0]:
                    data = formatted_brokercredentials[0]
                    def check_error(response):
                        if response.get('isError'):
                            return jsonify(response), 400
                        return None

                    token_response = get_token(cursor, data, user.id)
                    if (error := check_error(token_response)):
                        return error
                    
                    client_code = token_response.get('user_session').get('result', {}).get('clientCodes')
                    if client_code and client_code[0]:
                        data['client_code'] = client_code[0]
                        
                token = Token.get_token_by_user(cursor, user.id)
                if token:
                    column_names = ["id", "interactive_token", "userId", "market_token", "interactive_url"]
                    formatted_token = format_single_query_result(token, column_names)
                    
            return jsonify({"access_token": access_token, "user_data": user_data, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials, "token": formatted_token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500

def logout_user(cursor, email):
    try:
        user = User.find_by_email(cursor, email)
        if user:
            
            Settings.upsert_setting(cursor, {"userId": user.id, "predefined_mtm_sl" : None, "predefined_mtm_target" : None})
            Token.delete_tokens(cursor, user.id)
            
            return jsonify({"message": "User logged out successfully"}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred during logout", "error": str(e)}), 500
    
def preload_data(cursor, email):
    try:
        user = User.find_by_email(cursor, email)
        if user:
            user_data = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "country": user.country,
                "state": user.state,
                "city": user.city,
            }
            formatted_setting = None;
            formatted_brokercredentials = None;
            formatted_token = None;
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "limit_price",
                    "predefined_sl", "sl_type", "is_trailing", "predefined_target",
                    "target_type", "predefined_mtm_sl", "mtm_sl_type", "predefined_mtm_target",
                    "mtm_target_type", "lot_multiplier", "userId"
                ]
                formatted_setting = format_single_query_result(setting, column_names)
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.id)
            if brokercredentials:
                column_names = [
                    "id", "brokerServer", "MarketApiKey", "MarketSecretKey", "InteractiveApiKey", "InteractiveSecretKey", "MarketUrl", "InteractiveUrl", "userId", "interactiveUserId", "marketUserId", "client_code"
                ]
                formatted_brokercredentials = format_query_result(brokercredentials, column_names)
                
            token = Token.get_token_by_user(cursor, user.id)
            if token:
                column_names = ["id", "interactive_token", "userId", "market_token", "interactive_url"]
                formatted_token = format_single_query_result(token, column_names)
                
            return jsonify({"user_data": user_data, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials, "tokens": formatted_token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
