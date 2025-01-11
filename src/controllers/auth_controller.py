from flask import jsonify
from models.user_model import User
from models.settings_model import Settings
from models.xts_auth_model import XtsAuth
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

bcrypt = Bcrypt()

def register_user(cursor, username, password):
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        return jsonify({"message": "User registered successfully"}), 201
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while registering the user", "error": str(e)}), 500

def login_user(cursor, username, password):
    try:
        user = User.find_by_username(cursor, username)
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_jwt_token(identity=user.username)
            user_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email
            }
            formatted_setting = None;
            formatted_xts_auth = None;
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                column_names = [
                    "id", "theme_mode", "symbol", "open_order_type", "close_order_type",
                    "predefined_sl", "sl_type", "is_trailing", "predefined_target",
                    "target_type", "predefined_mtm_sl", "mtm_sl_type", "predefined_mtm_target",
                    "mtm_target_type", "lot_multiplier", "userId"
                ]
                formatted_setting = format_single_query_result(setting, column_names)
            xts_auth = XtsAuth.get_xts_auth_by_user(cursor, user.id)
            if xts_auth:
                print('xts_auth',xts_auth)
                column_names = [
                    "id", "MarketId", "MarketApiKey", "MarketSecretKey", "InteractiveApiKey", "InteractiveSecretKey", "userId"
                ]
                formatted_xts_auth = format_query_result(xts_auth, column_names)
            return jsonify({"access_token": access_token, "user_data": user_data, "setting": formatted_setting, "xts_auth": formatted_xts_auth}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
