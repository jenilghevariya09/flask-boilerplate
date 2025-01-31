from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)
    
class Settings:
    @staticmethod
    def create_setting(cursor, data):
        query = """
            INSERT INTO settings (
                theme_mode, symbol, open_order_type, limit_price, 
                predefined_sl, sl_type, is_trailing, predefined_target, 
                target_type, predefined_mtm_sl, mtm_sl_type, 
                predefined_mtm_target, mtm_target_type, lot_multiplier, userId, deleted
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Handle missing data by replacing missing keys with default or None
        values = (
            data.get('theme_mode', 'dark'),
            data.get('symbol', None),
            data.get('open_order_type', 'Market'),
            data.get('limit_price', 0),
            data.get('predefined_sl', None),
            data.get('sl_type', 'Points'),
            int(data.get('is_trailing', 0)),
            data.get('predefined_target', None),
            data.get('target_type', 'Points'),
            data.get('predefined_mtm_sl', None),
            data.get('mtm_sl_type', 'Points'),
            data.get('predefined_mtm_target', None),
            data.get('mtm_target_type', 'Points'),
            int(data.get('lot_multiplier', 1)),
            data.get('userId'),
            int(data.get('deleted', None)),
        )

        cursor.execute(query, values)

    @staticmethod
    def get_setting_by_userId(cursor, userId):
        query = "SELECT * FROM settings WHERE userId = %s AND deleted IS NULL"
        cursor.execute(query, (userId,))
        return cursor.fetchone()

    @staticmethod
    def update_setting(cursor, userId, data):
        query = "UPDATE settings SET "
        fields = []
        values = []

        if 'theme_mode' in data:
            fields.append("theme_mode = %s")
            values.append(data['theme_mode'])
        if 'symbol' in data:
            fields.append("symbol = %s")
            values.append(data['symbol'])
        if 'open_order_type' in data:
            fields.append("open_order_type = %s")
            values.append(data['open_order_type'])
        if 'limit_price' in data:
            fields.append("limit_price = %s")
            values.append(data['limit_price'])
        if 'predefined_sl' in data:
            fields.append("predefined_sl = %s")
            values.append(data['predefined_sl'])
        if 'sl_type' in data:
            fields.append("sl_type = %s")
            values.append(data['sl_type'])
        if 'is_trailing' in data:
            fields.append("is_trailing = %s")
            values.append(data['is_trailing'])
        if 'predefined_target' in data:
            fields.append("predefined_target = %s")
            values.append(data['predefined_target'])
        if 'target_type' in data:
            fields.append("target_type = %s")
            values.append(data['target_type'])
        if 'predefined_mtm_sl' in data:
            fields.append("predefined_mtm_sl = %s")
            values.append(data['predefined_mtm_sl'])
        if 'mtm_sl_type' in data:
            fields.append("mtm_sl_type = %s")
            values.append(data['mtm_sl_type'])
        if 'predefined_mtm_target' in data:
            fields.append("predefined_mtm_target = %s")
            values.append(data['predefined_mtm_target'])
        if 'mtm_target_type' in data:
            fields.append("mtm_target_type = %s")
            values.append(data['mtm_target_type'])
        if 'lot_multiplier' in data:
            fields.append("lot_multiplier = %s")
            values.append(data['lot_multiplier'])

        # Ensure we have fields to update
        if not fields:
            raise ValueError("No fields provided to update.")
        fields.append("deleted = %s")
        values.append(None)

        # Append WHERE clause
        query += ", ".join(fields) + " WHERE userId = %s"
        values.append(userId)

        # Execute the query
        cursor.execute(query, tuple(values))

    def delete_setting(cursor, userId):
    # Default values for the fields
        default_values = {
            'theme_mode': 'dark',
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
        }
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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
            'predefined_mtm_target', 'mtm_target_type', 'lot_multiplier'
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
            'theme_mode': 'dark',
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
        }

        # Prepare the values for the INSERT part
        insert_values = [
            data.get(field, default_values[field]) for field in allowed_fields
        ] + [user_id, None]

        # Add the update values for the ON DUPLICATE KEY UPDATE part
        query_values = insert_values + list(update_values.values())

        # Execute the query
        cursor.execute(query, query_values)


