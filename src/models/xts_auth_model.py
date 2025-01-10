from flask_mysqldb import MySQL

mysql = MySQL()

class XtsAuth:
    @staticmethod
    def create_xts_auth(cursor, data):
        query = """
            INSERT INTO xtsAuth (MarketId, MarketApiKey, MarketSecretKey, InteractiveApiKey, InteractiveSecretKey, userId)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data['MarketId'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], data['userId']))

    @staticmethod
    def get_xts_auth(cursor, xts_id):
        query = "SELECT * FROM xtsAuth WHERE id = %s"
        cursor.execute(query, (xts_id,))
        return cursor.fetchone()

    @staticmethod
    def update_xts_auth(cursor, xts_id, data):
        query = """
            UPDATE xtsAuth
            SET MarketId = %s, MarketApiKey = %s, MarketSecretKey = %s,
                InteractiveApiKey = %s, InteractiveSecretKey = %s
            WHERE id = %s
        """
        cursor.execute(query, (data['MarketId'], data['MarketApiKey'], data['MarketSecretKey'],
                               data['InteractiveApiKey'], data['InteractiveSecretKey'], xts_id))

    @staticmethod
    def delete_xts_auth(cursor, xts_id):
        query = "DELETE FROM xtsAuth WHERE id = %s"
        cursor.execute(query, (xts_id,))

    @staticmethod
    def get_xts_auth_by_user(cursor, user_id):
        query = "SELECT * FROM xtsAuth WHERE userId = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
