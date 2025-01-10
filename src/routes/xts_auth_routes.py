from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.xts_auth_controller import create_xts_auth, get_xts_auth, update_xts_auth, delete_xts_auth, get_xts_auth_by_user
from models.user_model import mysql, User

xts_auth_routes = Blueprint('xts_auth_routes', __name__)

# Create XtsAuth
@xts_auth_routes.route('/', methods=['POST'])
@jwt_required()
def create_xts():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400
        cursor = mysql.connection.cursor()
        response = create_xts_auth(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Get XtsAuth by ID
@xts_auth_routes.route('/<int:xts_id>', methods=['GET'])
@jwt_required()
def get_xts(xts_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_xts_auth(cursor, xts_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Update XtsAuth by ID
@xts_auth_routes.route('/<int:xts_id>', methods=['PUT'])
@jwt_required()
def update_xts(xts_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        cursor = mysql.connection.cursor()
        response = update_xts_auth(cursor, xts_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

# Delete XtsAuth by ID
@xts_auth_routes.route('/<int:xts_id>', methods=['DELETE'])
@jwt_required()
def delete_xts(xts_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_xts_auth(cursor, xts_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

# Get XtsAuth data by userId
@xts_auth_routes.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_xts_by_user(user_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_xts_auth_by_user(cursor, user_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
