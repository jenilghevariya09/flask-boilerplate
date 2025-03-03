from flask import Flask, request, jsonify
import random
import string
from botocore.exceptions import ClientError
from models.user_model import User
from models.settings_model import Settings
from models.broker_credentials_model import BrokerCredentials
from models.token import Token
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token
from utils.commonUtils import format_query_result, format_single_query_result , validate_password , verify_otp
from utils.httpUtils import HTTP
from utils.get_broker import get_token
from constant.constant import SETTING_COLUMN, TOKEN_COLUMN, BROKER_COLUMN
from flask_mail import Message
from datetime import datetime, timedelta
http = HTTP()

bcrypt = Bcrypt()

# Generate a 6-digit OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def register_user(cursor, data):
    try:
        password_errors = validate_password(data.get('password', ''))
        if password_errors:
            return jsonify({"success": False, "errors": " ".join(password_errors)}), 400

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
            Settings.upsert_setting(cursor, {"userId": user.id, "theme_mode" : 'light', "symbol": "NIFTY"})
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                formatted_setting = format_single_query_result(setting, SETTING_COLUMN)
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
            brokerType = None
            formatted_setting = None
            formatted_brokercredentials = None
            formatted_token = None
            Settings.upsert_setting(cursor, {"userId": user.id, "predefined_mtm_sl" : None, "predefined_mtm_target" : None})
            setting = Settings.get_setting_by_userId(cursor, user.id)
            if setting:
                formatted_setting = format_single_query_result(setting, SETTING_COLUMN)
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.id)
            if brokercredentials:
                formatted_brokercredentials = format_query_result(brokercredentials, BROKER_COLUMN)
                
                if formatted_brokercredentials and formatted_brokercredentials[0]:
                    data = formatted_brokercredentials[0]
                    brokerType = data.get('brokerServer')
                    if brokerType == 'Upstox':
                        return jsonify({"access_token": access_token, "user_data": user_data, "broker_type": brokerType, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials}), 200
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
                    formatted_token = format_single_query_result(token, TOKEN_COLUMN)
                    
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
                formatted_setting = format_single_query_result(setting, SETTING_COLUMN)
            brokercredentials = BrokerCredentials.get_broker_credentials_by_user(cursor, user.id)
            if brokercredentials:
                formatted_brokercredentials = format_query_result(brokercredentials, BROKER_COLUMN)
                if formatted_brokercredentials and formatted_brokercredentials[0]:
                    data = formatted_brokercredentials[0]
                    brokerType = data.get('brokerServer')
                    if brokerType == 'Upstox':
                        token = Token.get_token_by_user(cursor, user.id)
                        if token:
                            formatted_token = format_single_query_result(token, TOKEN_COLUMN)
                        return jsonify({"user_data": user_data, "broker_type": brokerType, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials, "tokens": formatted_token}), 200
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
                formatted_token = format_single_query_result(token, TOKEN_COLUMN)
                
            return jsonify({"user_data": user_data, "setting": formatted_setting, "brokercredentials": formatted_brokercredentials, "tokens": formatted_token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500

def update_password(cursor, email, old_password=None, otp=None, new_password=None):
    # Check if the user exists and verify the old password
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    user = User.find_by_email(cursor, email)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    # If old_password is provided, verify it
    if old_password:
        if not bcrypt.check_password_hash(user.password, old_password):
            return jsonify({'message': 'Old password is incorrect'}), 400

    # If OTP is provided, verify it
    elif otp:
        if not verify_otp(cursor, email, otp):  # Using the utility function
            return jsonify({'message': 'Invalid or expired OTP'}), 400
        # Delete OTP from DB after successful verification
    else:
        return jsonify({'message': 'Either old password or OTP is required'}), 400

    password_errors = validate_password(new_password)
    if password_errors:
        return jsonify({"success": False, "message": " ".join(password_errors)}), 400

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    new_password = hashed_password    # Update password (Use hashed password in production)
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
    cursor.execute("UPDATE users SET otp = NULL, otp_expiration = NULL WHERE email = %s", (email,))
    return jsonify({'message': 'Password changed successfully'}), 200
