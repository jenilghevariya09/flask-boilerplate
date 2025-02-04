from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()

class BrokerCredentials:
    @staticmethod
    def create_broker_credentials(cursor, data):
        user_id = data.get('userId')
        if not user_id:
            raise ValueError("user data is required for upserting brokercredentials.")  

        # Define allowed fields
        allowed_fields = [
            'userId', 'brokerServer', 'MarketApiKey', 'MarketSecretKey', 
            'InteractiveApiKey', 'InteractiveSecretKey', 'MarketUrl', 
            'InteractiveUrl', 'interactiveUserId', 'marketUserId', 'client_code'
        ]   

        # Ensure userId is present
        data['userId'] = user_id    

        # Extract fields from data that are allowed
        update_values = {key: data[key] for key in data if key in allowed_fields and data[key] is not None} 

        if not update_values:
            print("No valid fields to update, exiting function.")
            return  


        # Default values for missing fields (to avoid NULL insert issues)
        default_values = {field: "" for field in allowed_fields}  # Empty string instead of NULL    

        # Prepare the values for the INSERT part
        insert_values = [data.get(field, default_values[field]) for field in allowed_fields] + [None]  # 'deleted' = NULL   

        # Construct the INSERT query with placeholders
        insert_fields = allowed_fields + ['deleted']
        insert_placeholders = ', '.join(['%s'] * len(insert_fields))    

        # Construct the ON DUPLICATE KEY UPDATE clause dynamically
        update_clause = ', '.join(f"{field} = VALUES({field})" for field in update_values.keys())   

        query = f"""
            INSERT INTO brokercredentials ({', '.join(insert_fields)})
            VALUES ({insert_placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
        """ 
        # Execute the query
        cursor.execute(query, insert_values)    


    @staticmethod
    def get_broker_credentials(cursor, broker_id):
        query = "SELECT * FROM brokercredentials WHERE id = %s AND deleted IS NULL"
        cursor.execute(query, (broker_id,))
        return cursor.fetchone()

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
