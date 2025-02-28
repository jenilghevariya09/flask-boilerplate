from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.payment_history_controller import (
    create_payment_history, get_payment_history, update_payment_history, delete_payment_history, get_payment_history_by_user, get_all_payment_history
)
from models.payment_history_model import mysql
from models.user_model import User


payment_history_routes = Blueprint('payment_history_routes', __name__)

@payment_history_routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.get_user_by_email(cursor, email)
        data = request.json
        data['userId'] = user.get('id')
        response = create_payment_history(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@payment_history_routes.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get(payment_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_payment_history(cursor, payment_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500
    
@payment_history_routes.route('/getUsers', methods=['GET'])
@jwt_required()
def getUsers():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.get_user_by_email(cursor, email)
        response = get_payment_history_by_user(cursor, user.get('id'))
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500
    
@payment_history_routes.route('/all', methods=['GET'])
@jwt_required()
def getAll():
    try:
        cursor = mysql.connection.cursor()
        response = get_all_payment_history(cursor)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@payment_history_routes.route('/update/<int:payment_id>', methods=['POST'])
@jwt_required()
def update(payment_id):
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.get_user_by_email(cursor, email)
        data = request.json
        data['userId'] = user.get('id')
        
        response = update_payment_history(cursor, payment_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@payment_history_routes.route('/delete/<int:payment_id>', methods=['DELETE'])
@jwt_required()
def delete(payment_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_payment_history(cursor, payment_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500