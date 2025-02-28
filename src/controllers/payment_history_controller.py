from flask import jsonify
from models.payment_history_model import PaymentHistory

def create_payment_history(cursor, data):
    try:
        PaymentHistory.create_payment_history(cursor, data)
        return jsonify({"message": "Payment history created successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to create payment history.", "error": str(e)}), 500

def get_payment_history(cursor, payment_id):
    try:
        result = PaymentHistory.get_payment_history(cursor, payment_id)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "Payment history not found."}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payment history.", "error": str(e)}), 500
    
def get_all_payment_history(cursor):
    try:
        result = PaymentHistory.get_all_payment_history(cursor)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "Payment history not found."}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payment history.", "error": str(e)}), 500
    
def get_payment_history_by_user(cursor, userId):
    try:
        result = PaymentHistory.get_payment_history_by_user(cursor, userId)
        if result:
            return jsonify(result), 200
        return jsonify({"message": "Payment history not found."}), 404
    except Exception as e:
        return jsonify({"message": "Error retrieving payment history.", "error": str(e)}), 500

def update_payment_history(cursor, payment_id, data):
    try:
        PaymentHistory.update_payment_history(cursor, payment_id, data)
        return jsonify({"message": "Payment history updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to update payment history.", "error": str(e)}), 500

def delete_payment_history(cursor, payment_id):
    try:
        PaymentHistory.delete_payment_history(cursor, payment_id)
        return jsonify({"message": "Payment history deleted successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to delete payment history.", "error": str(e)}), 500