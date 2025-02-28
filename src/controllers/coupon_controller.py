from flask import jsonify
from models.coupon_model import Coupon

def create_coupon(cursor, data):
    try:
        existing_coupon = Coupon.get_coupon_by_code(cursor, data['code'])
        if existing_coupon:
            return jsonify({"message": "Coupon with this code already exists."}), 400
        
        Coupon.create_coupon(cursor, data)
        return jsonify({"message": "Coupon created successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to create coupon.", "error": str(e)}), 500
    
def get_all_coupons(cursor):
    try:
        coupons = Coupon.get_all_coupons(cursor)
        return jsonify(coupons), 200
    except Exception as e:
        return jsonify({"message": "Failed to fetch coupons.", "error": str(e)}), 500

def get_coupon_by_id(cursor, coupon_id):
    try:
        coupon = Coupon.get_coupon_by_id(cursor, coupon_id)
        if coupon:
            return jsonify(coupon), 200
        else:
            return jsonify({"message": "Coupon not found."}), 404
    except Exception as e:
        return jsonify({"message": "Failed to fetch coupon.", "error": str(e)}), 500

def toggle_coupon_status(cursor, coupon_id, is_active):
    try:
        Coupon.toggle_coupon_status(cursor, coupon_id, is_active)
        return jsonify({"message": "Coupon status updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to update coupon status.", "error": str(e)}), 500

def delete_coupon(cursor, coupon_id):
    try:
        coupon = Coupon.get_coupon_by_id(cursor, coupon_id)
        if not coupon:
            return jsonify({"message": "Coupon not found."}), 404
        if coupon['isActive']:
            return jsonify({"message": "Cannot delete an active coupon."}), 400
        
        Coupon.delete_coupon(cursor, coupon_id)
        return jsonify({"message": "Coupon deleted successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to delete coupon.", "error": str(e)}), 500
    
def update_coupon(cursor, coupon_id, data):
    try:
        existing_coupon = Coupon.get_coupon_by_id(cursor, coupon_id)
        if not existing_coupon:
            return jsonify({"message": "Coupon not found."}), 404
        
        Coupon.update_coupon(cursor, coupon_id, data)
        return jsonify({"message": "Coupon updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Failed to update coupon.", "error": str(e)}), 500