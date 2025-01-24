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
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        response = get_user_profile(cursor, email)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the profile", "error": str(e)}), 500

# Route to update the logged-in user's profile
@profile_routes.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        data = request.get_json()
        user = User.find_by_email(cursor, email)
        
        if user:
            response = update_user_profile(cursor, user.id, data)
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
@profile_routes.route('/<int:userId>', methods=['GET'])
@jwt_required()
def get_user_profile(userId):
    try:
        cursor = mysql.connection.cursor()
        response = get_user_by_id(cursor, userId)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the user profile", "error": str(e)}), 500
