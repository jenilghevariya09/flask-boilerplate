from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from controllers.coupon_controller import (
    create_coupon, get_all_coupons, get_coupon_by_id, toggle_coupon_status, delete_coupon, update_coupon
)
from models.coupon_model import mysql

coupon_routes = Blueprint('coupon_routes', __name__)

@coupon_routes.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = create_coupon(cursor, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@coupon_routes.route('/all', methods=['GET'])
@jwt_required()
def get_all():
    try:
        cursor = mysql.connection.cursor()
        response = get_all_coupons(cursor)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@coupon_routes.route('/<int:coupon_id>', methods=['GET'])
@jwt_required()
def get_by_id(coupon_id):
    try:
        cursor = mysql.connection.cursor()
        response = get_coupon_by_id(cursor, coupon_id)
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@coupon_routes.route('/toggle/<int:coupon_id>', methods=['PATCH'])
@jwt_required()
def toggle_status(coupon_id):
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        is_active = data.get('isActive', True)
        response = toggle_coupon_status(cursor, coupon_id, is_active)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@coupon_routes.route('/delete/<int:coupon_id>', methods=['DELETE'])
@jwt_required()
def delete(coupon_id):
    try:
        cursor = mysql.connection.cursor()
        response = delete_coupon(cursor, coupon_id)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500

@coupon_routes.route('/update/<int:coupon_id>', methods=['PUT'])
@jwt_required()
def update(coupon_id):
    try:
        cursor = mysql.connection.cursor()
        data = request.json
        response = update_coupon(cursor, coupon_id, data)
        mysql.connection.commit()
        cursor.close()
        return response
    except Exception as e:
        return jsonify({"message": "Unexpected error occurred.", "error": str(e)}), 500