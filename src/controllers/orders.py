from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from models.orders_model import Orders
from models.token import Token
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def create_order(cursor, user_id, order_data):
    try:
        # Required fields
        required_fields = {
             "status"
        }
        
        # Check if all required fields are present
        missing_fields = required_fields - set(order_data.keys())
        if missing_fields:
            return jsonify({"message": "Missing fields", "missing": list(missing_fields)}), 400
        
        # Call the model to insert the order
        order_id = Orders.create_order(cursor, user_id, order_data)
        
        if order_id:
            return jsonify({"message": "Order created successfully", "order_id": order_id}), 201
        else:
            return jsonify({"message": "Failed to create order"}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the order", "error": str(e)}), 500


def get_orders(cursor , user_id):
    try:
        result = Orders.get_orders(cursor , user_id)
        if result:
            return jsonify({"data":result,"message": 'Operation Executed Successfully'}), 200
        return jsonify({"message": "Orders not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving BrokerCredentials", "error": str(e)}), 500