from flask_mysqldb import MySQL

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)

class Token:
    @staticmethod
    def get_token_by_user(cursor, user_id):
        query = "SELECT * FROM tokens WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    
    @staticmethod
    def upsert_token(cursor, user_id, interactive_token=None, market_token=None, interactive_url=None):
        update_values = {}
        if interactive_token is not None and interactive_token != '':
            update_values['interactive_token'] = interactive_token
        if market_token is not None and market_token != '':
            update_values['market_token'] = market_token
        if interactive_url is not None and interactive_url != '':
            update_values['interactive_url'] = interactive_url

        query = """
            INSERT INTO tokens (user_id, interactive_token, market_token, interactive_url)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                {}
        """.format(', '.join('{} = %s'.format(key) for key in update_values))
        values = (
            user_id, interactive_token, market_token, interactive_url,
            *update_values.values()
        )
        cursor.execute(query, values)

