from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from socket_manager import emit_order_to_user  # Import function
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
            order_id = cursor.lastrowid  
        # Fetch the latest order details
            cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            new_order = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            new_order = dict(zip(column_names, new_order))
            emit_order_to_user(user_id, new_order)
            return order_id
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