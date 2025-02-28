from flask_mysqldb import MySQL
from utils.commonUtils import get_single_description_data, get_description_data_list
import json

mysql = MySQL()

class Coupon:
        
    @staticmethod
    def create_coupon(cursor, data):
        # Convert forPlans to JSON string if it's a list
        if 'forPlans' in data and isinstance(data['forPlans'], list):
            data['forPlans'] = json.dumps(data['forPlans'])
        if 'redeemedBy' in data and isinstance(data['redeemedBy'], list):
            data['redeemedBy'] = json.dumps(data['redeemedBy'])

        # Filter out keys with None values
        filtered_data = {k: v for k, v in data.items()}

        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join([f'%({key})s' for key in filtered_data.keys()])

        query = f"""
            INSERT INTO coupon ({columns})
            VALUES ({placeholders})
        """
        cursor.execute(query, filtered_data)
    
    @staticmethod
    def get_all_coupons(cursor):
        query = "SELECT * FROM coupon"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data
    
    @staticmethod
    def get_coupon_by_id(cursor, coupon_id):
        query = "SELECT * FROM coupon WHERE id = %s"
        cursor.execute(query, (coupon_id,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
    
    @staticmethod
    def get_coupon_by_code(cursor, coupon_code):
        query = "SELECT * FROM coupon WHERE code = %s"
        cursor.execute(query, (coupon_code,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
    
    @staticmethod
    def toggle_coupon_status(cursor, coupon_id, is_active):
        """Activate or deactivate a coupon based on `is_active` flag."""
        query = """
            UPDATE coupon
            SET isActive = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        cursor.execute(query, (is_active, coupon_id))
        
    @staticmethod
    def update_coupon(cursor, coupon_id, data):
        print('data',data)
        # Convert forPlans to JSON string if it's a list
        if 'forPlans' in data and isinstance(data['forPlans'], list):
            data['forPlans'] = json.dumps(data['forPlans'])
        if 'redeemedBy' in data and isinstance(data['redeemedBy'], list):
            data['redeemedBy'] = json.dumps(data['redeemedBy'])

        # Update only provided fields
        filtered_data = {k: v for k, v in data.items()}

        if not filtered_data:
            raise ValueError("No data provided for update.")

        # Dynamically generate SET clause
        set_clause = ', '.join([f"{key} = %({key})s" for key in filtered_data.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"

        query = f"""
            UPDATE coupon
            SET {set_clause}
            WHERE id = %(coupon_id)s
        """

        filtered_data['coupon_id'] = coupon_id
        cursor.execute(query, filtered_data)

    @staticmethod
    def delete_coupon(cursor, coupon_id):
        """Delete a coupon by its ID."""
        cursor.execute("DELETE FROM coupon WHERE id = %s", (coupon_id,))