from flask_mysqldb import MySQL

mysql = MySQL()

class BrokerCredentials:
    @staticmethod
    def create_broker_credentials(cursor, data):
        query = """
            INSERT INTO brokercredentials (brokerServer, MarketApiKey, MarketSecretKey, InteractiveApiKey, InteractiveSecretKey, MarketUrl, InteractiveUrl, userId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data['brokerServer'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['MarketUrl'], data['InteractiveUrl'], data['userId']))

    @staticmethod
    def get_broker_credentials(cursor, xts_id):
        query = "SELECT * FROM brokercredentials WHERE id = %s"
        cursor.execute(query, (xts_id,))
        return cursor.fetchone()

    @staticmethod
    def update_broker_credentials(cursor, xts_id, data):
        query = """
            UPDATE brokercredentials
            SET brokerServer = %s, MarketApiKey = %s, MarketSecretKey = %s,
                InteractiveApiKey = %s, InteractiveSecretKey = %s, MarketUrl = %s, InteractiveUrl = %s
            WHERE id = %s
        """
        cursor.execute(query, (data['brokerServer'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['MarketUrl'], data['InteractiveUrl'], xts_id))

    @staticmethod
    def delete_broker_credentials(cursor, xts_id):
        query = "DELETE FROM brokercredentials WHERE id = %s"
        cursor.execute(query, (xts_id,))

    @staticmethod
    def get_broker_credentials_by_user(cursor, user_id):
        query = "SELECT * FROM brokercredentials WHERE userId = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
