from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.broker_credentials import create_broker_credentials, get_broker_credentials, update_broker_credentials, delete_broker_credentials, get_broker_credentials_by_user
from models.user_model import mysql, User
from utils.get_broker import get_token

broker_credentials_routes = Blueprint('broker_credentials_routes', __name__)

# Create BrokerCredentials
@broker_credentials_routes.route('/upsert', methods=['POST'])
@jwt_required()
def upsert_broker():
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.find_by_email(cursor, email)
        data['userId'] = user.id
        
        def check_error(response):
            if response.get('isError'):
                return jsonify(response), 400
            return None

        token_response = get_token(cursor, data, user.id)
        if (error := check_error(token_response)):
            return error

        market_userId = token_response.get('market_data').get('result', {}).get('userID') 
        if market_userId:
            data['marketUserId'] = market_userId
            
        interactive_userId = token_response.get('user_session').get('result', {}).get('userID') 
        if interactive_userId:
            data['interactiveUserId'] = interactive_userId
        
        client_code = token_response.get('user_session').get('result', {}).get('clientCodes')
        if client_code and client_code[0]:
            data['client_code'] = client_code[0]

        # Create broker credentials
        response = create_broker_credentials(cursor, data)
        
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
@broker_credentials_routes.route('/get', methods=['GET'])
@jwt_required()
def get_broker_by_user():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.find_by_email(cursor, email)
        response = get_broker_credentials_by_user(cursor, user.id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
