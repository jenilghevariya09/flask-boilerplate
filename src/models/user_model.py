from flask_mysqldb import MySQL

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)

class User:
    def __init__(self, id, username, password, full_name=None, email=None):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email

    @staticmethod
    def find_by_username(cursor, username):
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        print('user---',user)
        return User(user[0], user[1], user[2], user[3], user[4]) if user else None

    @staticmethod
    def find_by_id(cursor, user_id):
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return User(user[0], user[1], user[2], user[3], user[4]) if user else None

    @staticmethod
    def update_profile(cursor, user_id, full_name, email):
        cursor.execute("""
            UPDATE users
            SET full_name = %s, email = %s
            WHERE id = %s
        """, (full_name, email, user_id))

    @staticmethod
    def get_all_users(cursor):
        query = "SELECT id, username, email, full_name FROM users"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_user_by_id(cursor, user_id):
        query = "SELECT id, username, email, full_name FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
