from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()

class Orders:
    
    @staticmethod
    def create_order(cursor, user_id, order_data):
        try:
            query = """
                INSERT INTO orders (
                    order_id, userid, instrument_token, exchange, transaction_type, quantity, 
                    validity, order_type, price, tag, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    instrument_token = VALUES(instrument_token),
                    exchange = VALUES(exchange),
                    transaction_type = VALUES(transaction_type),
                    quantity = VALUES(quantity),
                    validity = VALUES(validity),
                    order_type = VALUES(order_type),
                    price = VALUES(price),
                    tag = VALUES(tag),
                    status = VALUES(status)
            """
            
            values = (
                order_data.get("order_id", None),  # Use order_id if provided, else None
                user_id,
                order_data["instrument_token"],
                order_data["exchange"],
                order_data["transaction_type"],
                order_data["quantity"],
                order_data["validity"],
                order_data["order_type"],
                order_data["price"],
                order_data["tag"],
                order_data["status"]
            )

            cursor.execute(query, values)
            return cursor.lastrowid  # Returns last inserted/updated order ID

        except Exception as e:
            print("Error while inserting/updating order:", str(e))
            return None

    @staticmethod
    def get_orders(cursor, user_id):
        query = "SELECT * FROM orders WHERE userid = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        # Get column names from cursor.description
        column_names = [desc[0] for desc in cursor.description]
        
        # Convert result into a list of dictionaries
        orders = [dict(zip(column_names, row)) for row in rows]

        return orders

    @staticmethod
    def update_broker_credentials(cursor, broker_id, data):
        query = """
            UPDATE brokercredentials
            SET brokerServer = %s, MarketApiKey = %s, MarketSecretKey = %s,
                InteractiveApiKey = %s, InteractiveSecretKey = %s, MarketUrl = %s, InteractiveUrl = %s, interactiveUserId = %s, marketUserId = %s, client_code = %s deleted = NULL
            WHERE id = %s
        """
        cursor.execute(query, (data['brokerServer'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['MarketUrl'], data['InteractiveUrl'], data['interactiveUserId'], data['marketUserId'], data['client_code'], None, broker_id))
        
    @staticmethod
    def delete_broker_credentials(cursor, broker_id):
        # Default values for the fields
        default_values = {
            'brokerServer': None,
            'MarketApiKey': None,
            'MarketSecretKey': None,
            'InteractiveApiKey': None,
            'InteractiveSecretKey': None,
            'MarketUrl': None,
            'InteractiveUrl': None,
            'interactiveUserId': None,
            'marketUserId': None,
            'client_code': None,
        }   

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Construct the UPDATE query to set each column to its default value
        set_clause = ', '.join(f"{key} = %s" for key in default_values)

        query = f"""
            UPDATE brokercredentials
            SET {set_clause}, deleted = %s
            WHERE id = %s
        """ 

        # Prepare the values to update, including 'deleted' as 1 and default values for all fields
        values = tuple(default_values[key] for key in default_values) + (current_time, broker_id,)    

        # Execute the query
        cursor.execute(query, values)

    @staticmethod
    def get_broker_credentials_by_user(cursor, userId):
        query = "SELECT * FROM brokercredentials WHERE userId = %s AND deleted IS NULL"
        cursor.execute(query, (userId,))
        return cursor.fetchall()
