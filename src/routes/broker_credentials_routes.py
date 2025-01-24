from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.broker_credentials_controller import create_broker_credentials, get_broker_credentials, update_broker_credentials, delete_broker_credentials, get_broker_credentials_by_user
from models.user_model import mysql, User
from utils.callApi import call_host_lookup_api, call_user_session_api, call_user_market_api

broker_credentials_routes = Blueprint('broker_credentials_routes', __name__)

# Create BrokerCredentials
@broker_credentials_routes.route('/create', methods=['POST'])
@jwt_required()
def create_broker():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user_data = User.find_by_email(cursor, email)
        
        user_market_response = call_user_market_api(cursor, data, user_data.id)
        if user_market_response.get('type') == 'error':
            status_code = user_market_response.get('result').get('status') if user_market_response.get('result').get('status') else 500
            message = user_market_response.get('result').get('message') if user_market_response.get('result').get('message') else "An error occurred"
            return jsonify({"message": message, "error": user_market_response}), status_code

        host_lookup_response = call_host_lookup_api()
        if host_lookup_response.get('type') == 'error':
            status_code = host_lookup_response.get('result').get('status') if host_lookup_response.get('result').get('status') else 500
            message = host_lookup_response.get('result').get('message') if host_lookup_response.get('result').get('message') else "An error occurred"
            return jsonify({"message": message, "error": host_lookup_response}), status_code

        user_session_response = call_user_session_api(cursor, data, host_lookup_response, user_data.id)
        if user_session_response.get('type') == 'error':
            status_code = user_session_response.get('result').get('status') if user_session_response.get('result').get('status') else 500
            message = user_session_response.get('result').get('message') if user_session_response.get('result').get('message') else "An error occurred"
            return jsonify({"message": message, "error": user_session_response}), status_code
        
        response = create_broker_credentials(cursor, data, user_market_response, host_lookup_response, user_session_response)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Get BrokerCredentials by ID
@broker_credentials_routes.route('/<int:broker_id>', methods=['GET'])
@jwt_required()
def get_broker(broker_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_broker_credentials(cursor, broker_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Update BrokerCredentials by ID
@broker_credentials_routes.route('/<int:broker_id>', methods=['PUT'])
@jwt_required()
def update_broker(broker_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        cursor = mysql.connection.cursor()
        response = update_broker_credentials(cursor, broker_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Delete BrokerCredentials by ID
@broker_credentials_routes.route('/<int:broker_id>', methods=['DELETE'])
@jwt_required()
def delete_broker(broker_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_broker_credentials(cursor, broker_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Get BrokerCredentials data by userId
@broker_credentials_routes.route('/user/<int:userId>', methods=['GET'])
@jwt_required()
def get_broker_by_user(userId):
    try:
        cursor = mysql.connection.cursor()
        response = get_broker_credentials_by_user(cursor, userId)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
