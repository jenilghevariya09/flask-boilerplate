from flask import jsonify
from models.user_model import User
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result

def get_user_profile(cursor, email):
    try:
        user = User.find_by_email(cursor, email)
        if user:
            user_details = {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "country": user.country,
                "state": user.state,
                "city": user.city,
            }
            return jsonify({"data": user_details}), 200
        return jsonify({"message": "User not found"}), 404
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the profile", "error": str(e)}), 500

def update_user_profile(cursor, userId, data):
    try:
        User.update_profile(cursor, userId, data)
        return jsonify({"message": "Profile updated successfully"}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the profile", "error": str(e)}), 500

def get_all_users(cursor, page_no, page_limit):
    try:
        result = User.get_all_users(cursor)
        if result:
            column_names = ["id", "first_name", "last_name", "email", "phone_number" ]
            formatted_result = format_query_result(result, column_names)
            return jsonify({"data": formatted_result}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving users", "error": str(e)}), 500

def get_user_by_id(cursor, userId):
    try:
        result = User.get_user_by_id(cursor, userId)
        if result:
            column_names = ["id", "first_name", "last_name", "email", "phone_number" ]
            formatted_result = format_single_query_result(result, column_names)
            return jsonify({"data": formatted_result}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving User Profile", "error": str(e)}), 500
