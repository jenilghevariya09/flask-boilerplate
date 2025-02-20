from flask import jsonify
from models.user_model import User
from models.settings_model import Settings
from sqlalchemy.exc import SQLAlchemyError
from utils.commonUtils import format_query_result, format_single_query_result
from utils.httpUtils import HTTP
from constant.constant import SETTING_COLUMN

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
            formatted_setting = format_single_query_result(setting, SETTING_COLUMN)
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

def reset_setting(cursor, userId):
    try:
        Settings.reset_setting(cursor, userId)
        return jsonify({"message": "Setting deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while deleting the setting", "error": str(e)}), 500

def upsert_setting(cursor, data):
    try:
        Settings.upsert_setting(cursor, data)
        setting = Settings.get_setting_by_userId(cursor, data['userId'])
        if setting:
            formatted_setting = format_single_query_result(setting, SETTING_COLUMN)
            return jsonify(formatted_setting), 200
        return jsonify({"message": "Operation completed successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the setting", "error": str(e)}), 500