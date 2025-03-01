from flask_mysqldb import MySQL
from datetime import datetime, timezone
from utils.commonUtils import get_single_description_data

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)
    
class Settings:
    @staticmethod
    def create_setting(cursor, data):
        filtered_data = {k: v for k, v in data.items()}
        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join([f'%({key})s' for key in filtered_data.keys()])

        query = f"""
            INSERT INTO settings ({columns})
            VALUES ({placeholders})
        """
        cursor.execute(query, filtered_data)

    @staticmethod
    def get_setting_by_userId(cursor, userId):
        query = "SELECT * FROM settings WHERE userId = %s AND deleted IS NULL"
        cursor.execute(query, (userId,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data

    @staticmethod
    def update_setting(cursor, userId, data):
        filtered_data = {k: v for k, v in data.items()}
        set_clause = ', '.join([f"{key} = %({key})s" for key in filtered_data.keys()])

        query = f"""
            UPDATE payment_history
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(userId)s
        """
        filtered_data['userId'] = userId
        cursor.execute(query, filtered_data)

    def reset_setting(cursor, userId):
    # Default values for the fields
        default_values = {
            'theme_mode': 'light',
            'symbol': None,
            'open_order_type': 'Market',
            'limit_price': 0,
            'predefined_sl': None,
            'sl_type': 'Points',
            'is_trailing': 0,
            'predefined_target': None,
            'target_type': 'Points',
            'predefined_mtm_sl': None,
            'mtm_sl_type': 'Points',
            'predefined_mtm_target': None,
            'mtm_target_type': 'Points',
            'lot_multiplier': 1,
            'is_hedge': 1,
        }
        
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
        # Construct the UPDATE query to set each column to its default value
        set_clause = ', '.join(f"{key} = %s" for key in default_values)
        
        query = f"""
            UPDATE settings
            SET {set_clause}, deleted = %s
            WHERE userId = %s
        """
    
        # Prepare the values to update, including 'deleted' as 1 and default values for all fields
        values = tuple(default_values[key] for key in default_values)  + (current_time, userId)
    
        # Execute the query
        cursor.execute(query, values)

    @staticmethod
    def upsert_setting(cursor, data):
        # Extract the userId from the data; it's mandatory for the operation
        user_id = data.get('userId')
        if not user_id:
            raise ValueError("user data is required for upserting settings.")

        # Define the fields that can be updated
        allowed_fields = [
            'theme_mode', 'symbol', 'open_order_type', 'limit_price', 
            'predefined_sl', 'sl_type', 'is_trailing', 'predefined_target', 
            'target_type', 'predefined_mtm_sl', 'mtm_sl_type', 
            'predefined_mtm_target', 'mtm_target_type', 'lot_multiplier', 'is_hedge'
        ]

        # Filter the data to only include keys that are allowed fields
        update_values = {key: data[key] for key in data if key in allowed_fields}

        # If there are no fields to update, return early
        if not update_values:
            return

        # Construct the INSERT query with placeholders for all fields
        insert_fields = allowed_fields + ['userId', 'deleted']
        insert_placeholders = ', '.join(['%s'] * len(insert_fields))

        # Construct the ON DUPLICATE KEY UPDATE part dynamically
        update_clause = ', '.join(f'{field} = %s' for field in update_values.keys())
        update_clause += ', deleted = NULL'  

        query = f"""
            INSERT INTO settings ({', '.join(insert_fields)})
            VALUES ({insert_placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """

        # Default values for the INSERT part, populated with None or default values
        default_values = {
            'theme_mode': 'light',
            'symbol': 'NIFTY',
            'open_order_type': 'Market',
            'limit_price': 0,
            'predefined_sl': None,
            'sl_type': 'Points',
            'is_trailing': 0,
            'predefined_target': None,
            'target_type': 'Points',
            'predefined_mtm_sl': None,
            'mtm_sl_type': 'Points',
            'predefined_mtm_target': None,
            'mtm_target_type': 'Points',
            'lot_multiplier': 1,
            'is_hedge': 1,
        }

        # Prepare the values for the INSERT part
        insert_values = [
            data.get(field, default_values[field]) for field in allowed_fields
        ] + [user_id, None]

        # Add the update values for the ON DUPLICATE KEY UPDATE part
        query_values = insert_values + list(update_values.values())

        # Execute the query
        cursor.execute(query, query_values)


