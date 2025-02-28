from flask_mysqldb import MySQL
from utils.commonUtils import get_single_description_data

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)

class Token:
    @staticmethod
    def get_token_by_user(cursor, userId):
        query = "SELECT * FROM tokens WHERE userId = %s"
        cursor.execute(query, (userId,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
    
    @staticmethod
    def upsert_token(cursor, userId, interactive_token=None, market_token=None, interactive_url=None):
        update_values = {}
        if interactive_token is not None and interactive_token != '':
            update_values['interactive_token'] = interactive_token
        if market_token is not None and market_token != '':
            update_values['market_token'] = market_token
        if interactive_url is not None and interactive_url != '':
            update_values['interactive_url'] = interactive_url

        query = """
            INSERT INTO tokens (userId, interactive_token, market_token, interactive_url)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                {}
        """.format(', '.join('{} = %s'.format(key) for key in update_values))
        values = (
            userId, interactive_token, market_token, interactive_url,
            *update_values.values()
        )
        cursor.execute(query, values)

    @staticmethod
    def delete_tokens(cursor, userId):
        query = "DELETE FROM tokens WHERE userId = %s"
        cursor.execute(query, (userId,))