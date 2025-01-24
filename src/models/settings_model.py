from flask_mysqldb import MySQL

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)
    
class Settings:
    @staticmethod
    def create_setting(cursor, data):
        query = """
            INSERT INTO settings (
                theme_mode, symbol, open_order_type, close_order_type, 
                predefined_sl, sl_type, is_trailing, predefined_target, 
                target_type, predefined_mtm_sl, mtm_sl_type, 
                predefined_mtm_target, mtm_target_type, lot_multiplier, userId
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Handle missing data by replacing missing keys with default or None
        values = (
            data.get('theme_mode', 'dark'),
            data.get('symbol', None),
            data.get('open_order_type', 'Market'),
            data.get('close_order_type', 'Market'),
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
            data.get('userId')
        )

        cursor.execute(query, values)

    @staticmethod
    def get_setting_by_userId(cursor, userId):
        query = "SELECT * FROM settings WHERE userId = %s"
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
        if 'close_order_type' in data:
            fields.append("close_order_type = %s")
            values.append(data['close_order_type'])
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

        # Append WHERE clause
        query += ", ".join(fields) + " WHERE userId = %s"
        values.append(userId)

        # Execute the query
        cursor.execute(query, tuple(values))


    @staticmethod
    def delete_setting(cursor, userId):
        query = "DELETE FROM settings WHERE userId = %s"
        cursor.execute(query, (userId,))


    @staticmethod
    def upsert_setting(cursor, data):
        # Define the fields that need to be updated in case of a duplicate userId
        update_values = {}
        required_fields = [
            'theme_mode', 'symbol', 'open_order_type', 'close_order_type', 
            'predefined_sl', 'sl_type', 'is_trailing', 'predefined_target', 
            'target_type', 'predefined_mtm_sl', 'mtm_sl_type', 
            'predefined_mtm_target', 'mtm_target_type', 'lot_multiplier',
        ]

        for field in required_fields:
            update_values[field] = data.get(field)

        query = """
            INSERT INTO settings (
                theme_mode, symbol, open_order_type, close_order_type, 
                predefined_sl, sl_type, is_trailing, predefined_target, 
                target_type, predefined_mtm_sl, mtm_sl_type, 
                predefined_mtm_target, mtm_target_type, lot_multiplier, userId
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                {}
        """.format(', '.join('{} = %s'.format(key) for key in update_values))

        # Handle missing data by replacing missing keys with default or None
        values = (
            data.get('theme_mode', 'dark'),
            data.get('symbol', None),
            data.get('open_order_type', 'Market'),
            data.get('close_order_type', 'Market'),
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
            *update_values.values()  # Add the update values for the ON DUPLICATE KEY UPDATE
        )

        cursor.execute(query, values)

