from flask import jsonify
from models.user_model import User
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def get_user_profile(cursor, email):
    try:
        user = User.find_by_email(cursor, email)
        if user:
            return {
                "phone_number": user.phone_number,
                "first_name ": user.first_name,
                "last_name ": user.last_name,
                "email": user.email
            }, 200
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
            return http.response({"data":formatted_result},200, 'Operation Executed Successfully')
        return http.response({}, 404, 'No users found')
    except Exception as e:
        return http.response({}, 500, "An error occurred while retrieving users",str(e))

def get_user_by_id(cursor, userId):
    try:
        result = User.get_user_by_id(cursor, userId)
        if result:
            column_names = ["id", "first_name", "last_name", "email", "phone_number" ]
            formatted_result = format_single_query_result(result, column_names)
            return http.response({"data":formatted_result}, 200, 'Operation Executed Successfully')
        return http.response({}, 404, 'User not found')
    except Exception as e:
        return http.response({}, 500, "An error occurred while retrieving User Profile",str(e))
