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
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.find_by_email(cursor, email)
        data['userId'] = user.id
        
        # Helper function to handle API errors
        def check_error(response):
            if response.get('type') == 'error' or response.get('isError'):
                message = (response.get('result', {}).get('message') or 
                          response.get('description') or 
                          response.get('error') or 
                          "An error occurred")
                return jsonify({"message": message, "error": response}), 400
            return None

        # User Market API
        market_response = call_user_market_api(cursor, data, user.id)
        if (error := check_error(market_response)):
            return error
        if market_response.get('result', {}).get('userID'):
            data['marketUserId'] = market_response.get('result', {}).get('userID')

        # Host Lookup API
        host_response = call_host_lookup_api()
        if (error := check_error(host_response)):
            return error

        # User Session API
        session_response = call_user_session_api(cursor, data, host_response, user.id)
        if (error := check_error(session_response)):
            return error
        if session_response.get('result', {}).get('userID'):
            data['interactiveUserId'] = session_response.get('result', {}).get('userID')

        # Create broker credentials
        response = create_broker_credentials(cursor, data, market_response, host_response, session_response)
        
        mysql.connection.commit()
        return response

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()

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
