from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.broker_credentials_controller import create_broker_credentials, get_broker_credentials, update_broker_credentials, delete_broker_credentials, get_broker_credentials_by_user
from models.user_model import mysql, User

broker_credentials_routes = Blueprint('broker_credentials_routes', __name__)

# Create BrokerCredentials
@broker_credentials_routes.route('/create', methods=['POST'])
@jwt_required()
def create_xts():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400
        cursor = mysql.connection.cursor()
        response = create_broker_credentials(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Get BrokerCredentials by ID
@broker_credentials_routes.route('/<int:xts_id>', methods=['GET'])
@jwt_required()
def get_xts(xts_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_broker_credentials(cursor, xts_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Update BrokerCredentials by ID
@broker_credentials_routes.route('/<int:xts_id>', methods=['PUT'])
@jwt_required()
def update_xts(xts_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        cursor = mysql.connection.cursor()
        response = update_broker_credentials(cursor, xts_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Delete BrokerCredentials by ID
@broker_credentials_routes.route('/<int:xts_id>', methods=['DELETE'])
@jwt_required()
def delete_xts(xts_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_broker_credentials(cursor, xts_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Get BrokerCredentials data by userId
@broker_credentials_routes.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xts_by_user(user_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_broker_credentials_by_user(cursor, user_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
