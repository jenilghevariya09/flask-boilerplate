from flask import jsonify
from models.user_model import User
from models.settings_model import Settings
from models.broker_credentials_model import BrokerCredentials
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

bcrypt = Bcrypt()

def register_user(cursor, data):
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        data['password'] = hashed_password
        User.register_user(cursor, data)
        return jsonify({"message": "User registered successfully"}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while registering the user", "error": str(e)}), 500

def login_user(cursor, email, password):
    try:
        print(email)
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
            if brokercredentials:
                column_names = [
                    "id", "MarketId", "MarketApiKey", "MarketSecretKey", "InteractiveApiKey", "InteractiveSecretKey", "userId"
                ]
                formatted_brokercredentials = format_query_result(brokercredentials, column_names)
            return jsonify({"access_token": access_token, "user_data": user_data, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
