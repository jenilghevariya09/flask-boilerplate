from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.profile_controller import get_user_profile, update_user_profile, get_all_users, get_user_by_id
from models.user_model import mysql, User

profile_routes = Blueprint('profile_routes', __name__)

# Route to get the logged-in user's profile
@profile_routes.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        username = get_jwt_identity()
        cursor = mysql.connection.cursor()
        response = get_user_profile(cursor, username)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the profile", "error": str(e)}), 500

# Route to update the logged-in user's profile
@profile_routes.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        username = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('full_name') or not data.get('email'):
            return jsonify({'message': 'Full name and email are required'}), 400
        
        full_name = data.get('full_name')
        email = data.get('email')
        
        cursor = mysql.connection.cursor()
        user = User.find_by_username(cursor, username)
        
        if user:
            response = update_user_profile(cursor, user.id, full_name, email)
            mysql.connection.commit()
            cursor.close()
            return response
        
        cursor.close()
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the profile", "error": str(e)}), 500


# Get all users
@profile_routes.route('/all', methods=['GET'])
@jwt_required()
def get_users():
    try:
        cursor = mysql.connection.cursor()
        response = get_all_users(cursor)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving users", "error": str(e)}), 500

# Get user profile by ID
@profile_routes.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_user_by_id(cursor, user_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the user profile", "error": str(e)}), 500
