from flask_mysqldb import MySQL

mysql = MySQL()

class BrokerCredentials:
    @staticmethod
    def create_broker_credentials(cursor, data):
        update_values = {}
        required_fields = ['userId', 'brokerServer', 'MarketApiKey', 'MarketSecretKey', 'InteractiveApiKey', 'InteractiveSecretKey', 'MarketUrl', 'InteractiveUrl']
    
        for field in required_fields:
            update_values[field] = data.get(field)
    
        query = """
            INSERT INTO brokercredentials (userId, brokerServer, MarketApiKey, MarketSecretKey, InteractiveApiKey, InteractiveSecretKey, MarketUrl, InteractiveUrl)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                {}
        """.format(', '.join('{} = %s'.format(key) for key in update_values))
        values = (
            update_values['userId'], update_values['brokerServer'], update_values['MarketApiKey'], update_values['MarketSecretKey'], 
            update_values['InteractiveApiKey'], update_values['InteractiveSecretKey'], update_values['MarketUrl'], update_values['InteractiveUrl'],
            *update_values.values()
        )
        cursor.execute(query, values)

    @staticmethod
    def get_broker_credentials(cursor, broker_id):
        query = "SELECT * FROM brokercredentials WHERE id = %s"
        cursor.execute(query, (broker_id,))
        return cursor.fetchone()

    @staticmethod
    def update_broker_credentials(cursor, broker_id, data):
        query = """
            UPDATE brokercredentials
            SET brokerServer = %s, MarketApiKey = %s, MarketSecretKey = %s,
                InteractiveApiKey = %s, InteractiveSecretKey = %s, MarketUrl = %s, InteractiveUrl = %s
            WHERE id = %s
        """
        cursor.execute(query, (data['brokerServer'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['MarketUrl'], data['InteractiveUrl'], broker_id))

    @staticmethod
    def delete_broker_credentials(cursor, broker_id):
        query = "DELETE FROM brokercredentials WHERE id = %s"
        cursor.execute(query, (broker_id,))

    @staticmethod
    def get_broker_credentials_by_user(cursor, userId):
        query = "SELECT * FROM brokercredentials WHERE userId = %s"
        cursor.execute(query, (userId,))
        return cursor.fetchall()
