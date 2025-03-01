from flask import jsonify
from models.user_model import User
from models.plans_model import Plan
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

def get_user_profile(cursor, email):
    try:
        user = User.get_user_by_email(cursor, email)
        if user:
            plan = None
            if user.get('planId'):
                plan = Plan.get_plan_by_id(cursor, user.get('planId'))
                if user.get('status') == 'active' and user.get('expiryDate'):
                    expiry_date = user['expiryDate']
                    days_remaining = (expiry_date - datetime.now(timezone.utc)).days
                    plan['days_remaining'] = days_remaining
            return jsonify({"data": user, "planDetails": plan}), 200
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
            return jsonify({"data": result}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving users", "error": str(e)}), 500

def get_user_by_id(cursor, userId):
    try:
        result = User.get_user_by_id(cursor, userId)
        if result:
            return jsonify({"data": result}), 200
        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving User Profile", "error": str(e)}), 500
