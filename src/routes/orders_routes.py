from flask import Blueprint, request, jsonify
from controllers.orders import create_order , get_orders
orders_routes = Blueprint('orders_routes', __name__)
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import mysql, User
from utils.get_broker import get_token

@orders_routes.route('/create', methods=['POST'])
@jwt_required()
def create_order_route():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()

        # Get user details
        user = User.find_by_email(cursor, email)
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Get request data
        order_data = request.get_json()

        # Call the controller to handle order creation
        response = create_order(cursor, user.id, order_data)
        
        mysql.connection.commit()  # Commit transaction
        cursor.close()

        return response  # The controller will return the JSON response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@orders_routes.route('/get', methods=['GET'])
@jwt_required()
def get_orders_route():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user = User.find_by_email(cursor, email)
        response = get_orders(cursor , user.id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

