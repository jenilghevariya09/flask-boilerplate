from flask import jsonify
from models.payment_history_model import PaymentHistory
from models.plans_model import Plan

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
            plan_list = Plan.get_all_plan_list(cursor)
            if plan_list:
                plan_dict = {plan['id']: plan for plan in plan_list}  # Create a dictionary for quick lookup
                for item in result:
                    if 'planId' in item:
                        plan_id = item['planId']
                        if plan_id in plan_dict:
                            item['planDetails'] = plan_dict[plan_id]  # Append plan details to the item
    
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