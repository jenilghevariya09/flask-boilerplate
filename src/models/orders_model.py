from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from socket_manager import emit_order_to_user  # Import function
mysql = MySQL()

class Orders:
    
    @staticmethod
    def create_order(cursor, user_id, order_data):
        try:
            if 'order_id' in order_data:
                # If 'order_id' is provided, update the existing order with provided keys
                # Build the dynamic SET clause based on the provided keys
                set_clause = []
                values = []

                for key, value in order_data.items():
                    if key != "order_id":  # Don't include order_id in the SET clause
                        set_clause.append(f"{key} = %s")
                        values.append(value)

                # If no valid keys are passed for update, return None
                if not set_clause:
                    return None

                # Add the order_id at the end of the values for the WHERE clause
                set_clause_str = ", ".join(set_clause)
                query = f"""
                    UPDATE orders
                    SET {set_clause_str}
                    WHERE order_id = %s
                """
                values.append(order_data['order_id'])

                cursor.execute(query, tuple(values))
                cursor.connection.commit()  # Commit the transaction
                order_id = order_data['order_id']  # Fetch the last inserted order_id
                cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
                new_order = cursor.fetchone()
                column_names = [desc[0] for desc in cursor.description]
                new_order = dict(zip(column_names, new_order))
                emit_order_to_user(user_id, new_order)
                return order_id

            else:
                # If 'order_id' is not provided, create a new order
                query = """
                    INSERT INTO orders (
                        userid, instrument_token, exchange, transaction_type, quantity, 
                        validity, order_type, price, tag, status, average_price, order_timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    user_id,
                    order_data.get("instrument_token", None),
                    order_data.get("exchange", None),
                    order_data.get("transaction_type", None),
                    order_data.get("quantity", None),
                    order_data.get("validity", None),
                    order_data.get("order_type", None),
                    order_data.get("price", None),
                    order_data.get("tag", None),
                    order_data["status"],
                    order_data.get("average_price", None),
                    order_data.get("order_timestamp", None),
                )

                cursor.execute(query, values)
                cursor.connection.commit()  # Commit the transaction
                order_id = cursor.lastrowid  # Fetch the last inserted order_id
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