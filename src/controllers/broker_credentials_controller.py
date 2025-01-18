from flask import jsonify
from models.broker_credentials_model import BrokerCredentials
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def create_broker_credentials(cursor, data):
    try:
        BrokerCredentials.create_broker_credentials(cursor, data)
        return jsonify({"message": "BrokerCredentials created successfully"}), 201
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while creating BrokerCredentials", "error": str(e)}), 500

def get_broker_credentials(cursor, xts_id):
    try:
        result = BrokerCredentials.get_broker_credentials(cursor, xts_id)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "BrokerCredentials not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving BrokerCredentials", "error": str(e)}), 500

def update_broker_credentials(cursor, xts_id, data):
    try:
        BrokerCredentials.update_broker_credentials(cursor, xts_id, data)
        return jsonify({"message": "BrokerCredentials updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating BrokerCredentials", "error": str(e)}), 500

def delete_broker_credentials(cursor, xts_id):
    try:
        BrokerCredentials.delete_broker_credentials(cursor, xts_id)
        return jsonify({"message": "BrokerCredentials deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting BrokerCredentials", "error": str(e)}), 500

def get_broker_credentials_by_user(cursor, user_id):
    try:
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, user_id)
        if result:
            column_names = ["id", "MarketId", "MarketApiKey", "MarketSecretKey","InteractiveApiKey", "InteractiveSecretKey", "userId"]
            formatted_result = format_query_result(result, column_names)
            return http.response({"data":formatted_result},200, 'Operation Executed Successfully')
        return jsonify({"message": "No BrokerCredentials data found for this user"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving BrokerCredentials data", "error": str(e)}), 500
