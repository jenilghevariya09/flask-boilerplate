from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.settings import create_setting, get_setting_by_userId, update_setting, delete_setting, upsert_setting
from models.settings_model import mysql
from models.user_model import mysql, User
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

@settings_routes.route('/getSetting', methods=['GET'])
@jwt_required()
def get():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user_data = User.find_by_email(cursor, email)
        response = get_setting_by_userId(cursor, user_data.id)
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

@settings_routes.route('/delete', methods=['DELETE'])
@jwt_required()
def delete():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user_data = User.find_by_email(cursor, email)
        response = delete_setting(cursor, user_data.id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@settings_routes.route('/upsert', methods=['POST'])
@jwt_required()
def upsert():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user_data = User.find_by_email(cursor, email)
        data = request.json
        data['userId'] = user_data.id
        response = upsert_setting(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500