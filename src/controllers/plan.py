from flask import jsonify
from models.plans_model import Plan
from datetime import datetime, timedelta

def can_purchase_plan(user_data, plan):
    subscription_days_map = {'monthly': 31, 'annual': 366, 'twoYear': 731}
    subscription_days = subscription_days_map.get(plan.get('subscriptionPeriod'), 0)
    
    expiry_date = user_data.get('expiryDate')
    new_expiry_date = expiry_date + timedelta(days=subscription_days)
    max_allowed_date = datetime.today() + timedelta(days=741)  # 2 years + 10 days buffer
    if user_data.get('status') == 'active' and new_expiry_date > max_allowed_date:
        return False  # Cannot purchase plan
    
    return True  # Allowed to purchase plan

def create_plan(cursor, data):
    try:
        Plan.create_plan(cursor, data)
        return jsonify({"message": "Plan created successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the plan", "error": str(e)}), 500


def get_plan_by_id(cursor, plan_id):
    try:
        plan = Plan.get_plan_by_id(cursor, plan_id)
        if plan:
            return jsonify(plan), 200
        return jsonify({"message": "Plan not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the plan", "error": str(e)}), 500
    
def get_plans(cursor, user_data):
    try:
        plans = Plan.get_all_plans(cursor)
        if plans:
            if user_data.get('status') == 'active' and user_data.get('expiryDate'):
                purchasable_plans = [plan for plan in plans if can_purchase_plan(user_data, plan)]
                if not purchasable_plans:
                    return jsonify([]), 200
                return jsonify(purchasable_plans), 200
            return jsonify(plans), 200
        return jsonify({"message": "Plan not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the plan", "error": str(e)}), 500


def update_plan(cursor, plan_id, data):
    try:
        Plan.update_plan(cursor, plan_id, data)
        return jsonify({"message": "Plan updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the plan", "error": str(e)}), 500


def activate_deactivate_plan(cursor, plan_id, is_active):
    try:
        Plan.set_plan_active_status(cursor, plan_id, is_active)
        status = "activated" if is_active else "deactivated"
        return jsonify({"message": f"Plan {status} successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the plan status", "error": str(e)}), 500

def delete_plan(cursor, plan_id):
    try:
        plan = Plan.get_plan_by_id(cursor, plan_id)
        if not plan:
            return jsonify({"message": "Plan not found"}), 404
        if plan['isActive']:
            return jsonify({"message": "Cannot delete an active plan"}), 400
        
        Plan.delete_plan(cursor, plan_id)
        return jsonify({"message": "Plan deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting the plan", "error": str(e)}), 500