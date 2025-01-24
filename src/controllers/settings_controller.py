from flask import jsonify
from models.user_model import User
from models.settings_model import Settings
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP

http = HTTP()

def create_setting(cursor, data):
    try:
        Settings.create_setting(cursor, data)
        return jsonify({"message": "Setting created successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the setting", "error": str(e)}), 500

def get_setting_by_userId(cursor, userId):
    try:
        setting = Settings.get_setting_by_userId(cursor, userId)
        if setting:
            column_names = [
                "id", "theme_mode", "symbol", "open_order_type", "close_order_type",
                "predefined_sl", "sl_type", "is_trailing", "predefined_target",
                "target_type", "predefined_mtm_sl", "mtm_sl_type", "predefined_mtm_target",
                "mtm_target_type", "lot_multiplier", "userId"
            ]
            formatted_setting = format_single_query_result(setting, column_names)
            return jsonify(formatted_setting), 200
        return jsonify({"message": "Setting not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while retrieving the setting", "error": str(e)}), 500

def update_setting(cursor, userId, data):
    try:
        Settings.update_setting(cursor, userId, data)
        return jsonify({"message": "Setting updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the setting", "error": str(e)}), 500

def delete_setting(cursor, userId):
    try:
        Settings.delete_setting(cursor, userId)
        return jsonify({"message": "Setting deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting the setting", "error": str(e)}), 500

def upsert_setting(cursor, data):
    try:
        Settings.upsert_setting(cursor, data)
        return jsonify({"message": "Operation completed successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the setting", "error": str(e)}), 500