from flask import jsonify
from models.broker_credentials_model import BrokerCredentials
from sqlalchemy.exc import SQLAlchemyError
from models.token import Token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def create_broker_credentials(cursor, data):
    try:
        BrokerCredentials.create_broker_credentials(cursor, data)
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, data.get('userId'))
        if result:
            token = Token.get_token_by_user(cursor, data.get('userId'))
            return jsonify({"data": result, "token": token, "message": "BrokerCredentials created successfully"}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while creating BrokerCredentials", "error": str(e)}), 500

def get_broker_credentials(cursor, broker_id):
    try:
        result = BrokerCredentials.get_broker_credentials(cursor, broker_id)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "BrokerCredentials not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving BrokerCredentials", "error": str(e)}), 500

def update_broker_credentials(cursor, broker_id, data):
    try:
        BrokerCredentials.update_broker_credentials(cursor, broker_id, data)
        return jsonify({"message": "BrokerCredentials updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating BrokerCredentials", "error": str(e)}), 500

def delete_broker_credentials(cursor, broker_id):
    try:
        BrokerCredentials.delete_broker_credentials(cursor, broker_id)
        return jsonify({"message": "BrokerCredentials deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting BrokerCredentials", "error": str(e)}), 500

def get_broker_credentials_by_user(cursor, userId):
    try:
        result = BrokerCredentials.get_broker_credentials_by_user(cursor, userId)
        if result and result[0]:
            return jsonify({"data":result[0],"message": 'Operation Executed Successfully'}), 200
        return jsonify({"message": "No BrokerCredentials data found for this user"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving BrokerCredentials data", "error": str(e)}), 500
