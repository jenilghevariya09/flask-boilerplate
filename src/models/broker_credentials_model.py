from flask_mysqldb import MySQL
from datetime import datetime

mysql = MySQL()

class BrokerCredentials:
    @staticmethod
    def create_broker_credentials(cursor, data):
        update_values = {}
        required_fields = ['userId', 'brokerServer', 'MarketApiKey', 'MarketSecretKey', 'InteractiveApiKey', 'InteractiveSecretKey', 'MarketUrl', 'InteractiveUrl', 'interactiveUserId', 'marketUserId']
    
        for field in required_fields:
            update_values[field] = data.get(field)
    
        query = """
            INSERT INTO brokercredentials (userId, brokerServer, MarketApiKey, MarketSecretKey, InteractiveApiKey, InteractiveSecretKey, MarketUrl, InteractiveUrl, interactiveUserId, marketUserId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                {}, deleted = NULL
        """.format(', '.join('{} = %s'.format(key) for key in update_values))
        values = (
            update_values['userId'], update_values['brokerServer'], update_values['MarketApiKey'], update_values['MarketSecretKey'], 
            update_values['InteractiveApiKey'], update_values['InteractiveSecretKey'], update_values['MarketUrl'], update_values['InteractiveUrl'],
            update_values['interactiveUserId'], update_values['marketUserId'], None,
            *update_values.values()
        )
        cursor.execute(query, values)

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
                InteractiveApiKey = %s, InteractiveSecretKey = %s, MarketUrl = %s, InteractiveUrl = %s, interactiveUserId = %s, marketUserId = %s, deleted = NULL
            WHERE id = %s
        """
        cursor.execute(query, (data['brokerServer'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['MarketUrl'], data['InteractiveUrl'], data['interactiveUserId'], data['marketUserId'], None, broker_id))
        
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
