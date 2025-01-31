from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.auth import register_user, login_user, logout_user
from models.user_model import mysql

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