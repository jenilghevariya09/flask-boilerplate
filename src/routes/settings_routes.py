from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from controllers.settings_controller import create_setting, get_setting_by_userId, update_setting, delete_setting
from models.settings_model import mysql
settings_routes = Blueprint('settings_routes', __name__)

@settings_routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = create_setting(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@settings_routes.route('/<int:userId>', methods=['GET'])
@jwt_required()
def get(userId):
    try:
        cursor = mysql.connection.cursor()
        response = get_setting_by_userId(cursor, userId)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@settings_routes.route('/update/<int:userId>', methods=['POST'])
@jwt_required()
def update(userId):
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = update_setting(cursor, userId, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@settings_routes.route('/<int:userId>', methods=['DELETE'])
@jwt_required()
def delete(userId):
    try:
        cursor = mysql.connection.cursor()
        response = delete_setting(cursor, userId)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
