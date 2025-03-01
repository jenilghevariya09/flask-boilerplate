from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.plan import create_plan, get_plan_by_id, update_plan, activate_deactivate_plan, delete_plan, get_plans
from models.plans_model import mysql
from models.user_model import User

plan_routes = Blueprint('plan_routes', __name__)

@plan_routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = create_plan(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        print('e',e)
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@plan_routes.route('/get/<int:plan_id>', methods=['GET'])
@jwt_required()
def get(plan_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_plan_by_id(cursor, plan_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
    
@plan_routes.route('/allPlans', methods=['GET'])
@jwt_required()
def get_all():
    try:
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        user_data = User.get_user_by_email(cursor, email)
        response = get_plans(cursor, user_data)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@plan_routes.route('/update/<int:plan_id>', methods=['POST'])
@jwt_required()
def update(plan_id):
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = update_plan(cursor, plan_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@plan_routes.route('/setStatus/<int:plan_id>', methods=['POST'])
@jwt_required()
def set_status(plan_id):
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        is_active = data.get("isActive")
        response = activate_deactivate_plan(cursor, plan_id, is_active)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
    
@plan_routes.route('/delete/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete(plan_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_plan(cursor, plan_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500