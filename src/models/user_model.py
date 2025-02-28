from flask_mysqldb import MySQL
from utils.commonUtils import get_single_description_data, get_description_data_list

mysql = MySQL()

def init_app(app):
    mysql.init_app(app)

class User:
    def __init__(self, id, first_name, last_name, email, phone_number, password, country, state, city, created_at, updated_at):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.country = country
        self.state = state
        self.city = city
        self.created_at = created_at
        self.updated_at = updated_at
        
    @staticmethod
    def register_user(cursor, data):
        query = """
            INSERT INTO users (
                first_name, last_name, email, phone_number, 
                password, country, state, city, status, trialDate
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('first_name', None),
            data.get('last_name', None),
            data.get('email', None),
            data.get('phone_number', None),
            data.get('password', None),
            data.get('country', 'India'),
            data.get('state', None),
            data.get('city', None),
            data.get('status', None),
            data.get('trialDate', None),
        )

        cursor.execute(query, values)
        
    @staticmethod
    def find_by_email(cursor, email):
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data

    @staticmethod
    def find_by_id(cursor, userId):
        cursor.execute("SELECT * FROM users WHERE id = %s", (userId,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data
        
    @staticmethod
    def update_profile(cursor, userId, data):
        # Update only provided fields
        filtered_data = {k: v for k, v in data.items()}
        set_clause = ', '.join([f"{key} = %({key})s" for key in filtered_data.keys()])

        query = f"""
            UPDATE users
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(userId)s
        """
        filtered_data['userId'] = userId
        cursor.execute(query, filtered_data)

    @staticmethod
    def get_all_users(cursor):
        query = "SELECT * FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()
        data = get_description_data_list(cursor, rows)
        return data

    @staticmethod
    def get_user_by_id(cursor, userId):
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (userId,))
        row = cursor.fetchone()
        data = get_single_description_data(cursor, row)
        return data

    @staticmethod
    def get_user_by_email(cursor, email):
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        if row:
            column_names = [desc[0] for desc in cursor.description]
            user = dict(zip(column_names, row))
            user.pop('password', None)
            return user
        return None
    