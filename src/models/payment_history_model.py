from flask_mysqldb import MySQL
from utils.commonUtils import get_single_description_data, get_description_data_list

mysql = MySQL()
class PaymentHistory:

    @staticmethod
    def create_payment_history(cursor, data):
        # Filter out keys with None values
        filtered_data = {k: v for k, v in data.items()}
        columns = ', '.join(filtered_data.keys())
        placeholders = ', '.join([f'%({key})s' for key in filtered_data.keys()])

        query = f"""
            INSERT INTO payment_history ({columns})
            VALUES ({placeholders})
        """
        cursor.execute(query, filtered_data)
        last_id = cursor.lastrowid  # Get the last inserted ID

        if last_id:
            cursor.execute("SELECT * FROM payment_history WHERE id = %s", (last_id,))
            row = cursor.fetchone()
            data = get_single_description_data(cursor, row)
            return data

        return None

    @staticmethod
    def get_all_payment_history(cursor):
        query = "SELECT * FROM payment_history"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data

    @staticmethod
    def get_payment_history(cursor, id):
        query = "SELECT * FROM payment_history WHERE id = %s"
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
    
    @staticmethod
    def get_payment_history_by_paymentId(cursor, paymentId):
        query = "SELECT * FROM payment_history WHERE paymentId = %s"
        cursor.execute(query, (paymentId,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
    
    @staticmethod
    def get_payment_history_by_user(cursor, userId):
        query = "SELECT * FROM payment_history WHERE userId = %s ORDER BY created_at DESC"
        cursor.execute(query, (userId,))
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data

    @staticmethod
    def update_payment_history(cursor, payment_id, data):
        # Update only provided fields
        filtered_data = {k: v for k, v in data.items()}
        set_clause = ', '.join([f"{key} = %({key})s" for key in filtered_data.keys()])

        query = f"""
            UPDATE payment_history
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(payment_id)s
        """
        filtered_data['payment_id'] = payment_id
        cursor.execute(query, filtered_data)

    @staticmethod
    def delete_payment_history(cursor, payment_id):
        cursor.execute("DELETE FROM payment_history WHERE id = %s", (payment_id,))