from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.auth import register_user, login_user, logout_user, preload_data , update_password
from models.user_model import mysql
from utils.commonUtils import verify_otp , send_otp_email

auth_routes = Blueprint('auth_routes', __name__)

# Route for User Registration
@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = register_user(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Route for User Login
@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'email and password are required'}), 400
        
        email = data.get('email')
        password = data.get('password')
        cursor = mysql.connection.cursor()
        response = login_user(cursor, email, password)
        mysql.connection.commit()
        cursor.close()

        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@auth_routes.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        response = logout_user(cursor, email)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    
@auth_routes.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        data = request.get_json()
        email = get_jwt_identity()
        if not data.get('new_password'):
            return jsonify({'message': 'new_password is required'}), 400

        old_password = data.get('old_password')
        otp = data.get('otp')  # Accept OTP as an alternative
        new_password = data.get('new_password')

        if not old_password and not otp:
            return jsonify({'message': 'Either old_password or OTP is required'}), 400

        cursor = mysql.connection.cursor()
        response = update_password(cursor, email, old_password, otp, new_password)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500    
@auth_routes.route('/preload', methods=['GET'])
@jwt_required()
def preload():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        response = preload_data(cursor, email)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@auth_routes.route('/send-emailOtp', methods=['GET'])
@jwt_required()
def send_otp():
    try:
        data = request.get_json()
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        response = send_otp_email(cursor, email)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@auth_routes.route('/verify-otp', methods=['POST'])
@jwt_required()
def verify():
    try:
        data = request.get_json()
        email = get_jwt_identity()
        otp = data.get('otp')
        verification_type = data.get('verification_type')
        if not otp or not verification_type:
            return jsonify({"message": "OTP and verification_type are required"}), 400
        cursor = mysql.connection.cursor()
        is_valid_otp = verify_otp(cursor, email, otp)
        print("is_valid_otp" , is_valid_otp)
        if not is_valid_otp:
            return jsonify({"message": "Invalid or expired OTP"}), 400
        if verification_type == "email":
            cursor.execute("UPDATE users SET isEmailVerified = TRUE WHERE email = %s", (email,))
        elif verification_type == "mobile":
            cursor.execute("UPDATE users SET isMobileVerified = TRUE WHERE email = %s", (email,))
        else:
            return jsonify({"message": "Invalid verification_type"}), 400
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": f"{verification_type.capitalize()} verified successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500