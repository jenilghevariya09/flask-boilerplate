from flask import jsonify
from models.xts_auth_model import XtsAuth
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def create_xts_auth(cursor, data):
    try:
        XtsAuth.create_xts_auth(cursor, data)
        return jsonify({"message": "XtsAuth created successfully"}), 201
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while creating XtsAuth", "error": str(e)}), 500

def get_xts_auth(cursor, xts_id):
    try:
        result = XtsAuth.get_xts_auth(cursor, xts_id)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "XtsAuth not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving XtsAuth", "error": str(e)}), 500

def update_xts_auth(cursor, xts_id, data):
    try:
        XtsAuth.update_xts_auth(cursor, xts_id, data)
        return jsonify({"message": "XtsAuth updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating XtsAuth", "error": str(e)}), 500

def delete_xts_auth(cursor, xts_id):
    try:
        XtsAuth.delete_xts_auth(cursor, xts_id)
        return jsonify({"message": "XtsAuth deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting XtsAuth", "error": str(e)}), 500

def get_xts_auth_by_user(cursor, user_id):
    try:
        result = XtsAuth.get_xts_auth_by_user(cursor, user_id)
        if result:
            column_names = ["id", "MarketId", "MarketApiKey", "MarketSecretKey","InteractiveApiKey", "InteractiveSecretKey", "userId"]
            formatted_result = format_query_result(result, column_names)
            return http.response({"data":formatted_result},200, 'Operation Executed Successfully')
        return jsonify({"message": "No XtsAuth data found for this user"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving XtsAuth data", "error": str(e)}), 500
