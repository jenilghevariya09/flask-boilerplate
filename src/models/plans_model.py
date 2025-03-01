from flask_mysqldb import MySQL
from datetime import datetime
import json
from utils.commonUtils import get_single_description_data, get_description_data_list

mysql = MySQL()

class Plan:
    @staticmethod
    def create_plan(cursor, data):
        # Convert featureLists to JSON string if it's a list
        if 'featureLists' in data and isinstance(data['featureLists'], list):
            data['featureLists'] = json.dumps(data['featureLists'])

        # Filter out keys with None values
        filtered_data = {k: v for k, v in data.items()}

        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join([f'%({key})s' for key in filtered_data.keys()])

        query = f"""
            INSERT INTO plans ({columns})
            VALUES ({placeholders})
        """
        cursor.execute(query, filtered_data)

    @staticmethod
    def get_plan_by_id(cursor, plan_id):
        query = "SELECT * FROM plans WHERE id = %s"
        cursor.execute(query, (plan_id,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data

    @staticmethod
    def get_all_plans(cursor):
        query = "SELECT * FROM plans WHERE isActive = TRUE"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data
    
    @staticmethod
    def get_all_plan_list(cursor):
        query = "SELECT * FROM plans"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data
    
    @staticmethod
    def update_plan(cursor, plan_id, data):
        # Convert featureLists to JSON string if it's a list
        if 'featureLists' in data and isinstance(data['featureLists'], list):
            data['featureLists'] = json.dumps(data['featureLists'])

        # Update only provided fields
        filtered_data = {k: v for k, v in data.items()}

        if not filtered_data:
            raise ValueError("No data provided for update.")

        # Dynamically generate SET clause
        set_clause = ', '.join([f"{key} = %({key})s" for key in filtered_data.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"  # ✅ Append updated_at without a trailing comma issue

        query = f"""
            UPDATE plans
            SET {set_clause}
            WHERE id = %(plan_id)s
        """

        filtered_data['plan_id'] = plan_id
        cursor.execute(query, filtered_data)

    @staticmethod
    def delete_plan(cursor, plan_id):
        query = "DELETE FROM plans WHERE id = %s"
        cursor.execute(query, (plan_id,))
        
    @staticmethod
    def set_plan_active_status(cursor, plan_id, is_active: bool):

        query = """
            UPDATE plans
            SET isActive = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (is_active, plan_id))

