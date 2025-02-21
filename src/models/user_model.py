from flask_mysqldb import MySQL

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
                password, country, state, city
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
        )

        cursor.execute(query, values)
        
    @staticmethod
    def find_by_email(cursor, email):
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return User(user[0], user[1], user[2], user[3], user[4],user[5], user[6], user[7], user[8], user[9], user[10]) if user else None

    @staticmethod
    def find_by_id(cursor, userId):
        cursor.execute("SELECT * FROM users WHERE id = %s", (userId,))
        user = cursor.fetchone()
        return User(user[0], user[1], user[2], user[3], user[4],user[5], user[6], user[7], user[8], user[9], user[10]) if user else None

    @staticmethod
    def update_profile(cursor, userId, data):
        updatable_fields = ['first_name', 'last_name', 'email', 'phone_number', 'country', 'state', 'city']
        fields = []
        values = []

        for field in updatable_fields:
            if field in data:
                fields.append(f"{field} = %s")
                values.append(data[field])

        if not fields:
            raise ValueError("No fields provided to update.")

        fields.append("updated_at = NOW()")
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        values.append(userId)

        cursor.execute(query, tuple(values))

    @staticmethod
    def get_all_users(cursor):
        query = "SELECT * FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        users = [dict(zip(column_names, row)) for row in rows]
        return users

    @staticmethod
    def get_user_by_id(cursor, userId):
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (userId,))
        row = cursor.fetchone()
        if row:
            column_names = [desc[0] for desc in cursor.description]
            user = dict(zip(column_names, row))
            return user
        return None

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
    