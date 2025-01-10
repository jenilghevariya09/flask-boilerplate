from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.auth_controller import register_user, login_user
from models.user_model import mysql

auth_routes = Blueprint('auth_routes', __name__)

# Route for User Registration
@auth_routes.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        cursor = mysql.connection.cursor()
        response = register_user(cursor, username, password)
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
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        cursor = mysql.connection.cursor()
        response = login_user(cursor, username, password)
        cursor.close()

        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
