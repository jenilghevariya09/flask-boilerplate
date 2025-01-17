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

        if not fields:
            raise ValueError("No fields provided to update.")
        # Handle missing data by replacing missing keys with default or None
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
    def find_by_id(cursor, user_id):
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return User(user[0], user[1], user[2], user[3], user[4],user[5], user[6], user[7], user[8], user[9], user[10]) if user else None

    @staticmethod
    def update_profile(cursor, userId, data):
        query = "UPDATE users SET "
        fields = []
        values = []

        if 'first_name' in data:
            fields.append("first_name = %s")
            values.append(data['first_name'])
        if 'last_name' in data:
            fields.append("last_name = %s")
            values.append(data['last_name'])
        if 'email' in data:
            fields.append("email = %s")
            values.append(data['email'])
        if 'phone_number' in data:
            fields.append("phone_number = %s")
            values.append(data['phone_number'])
        if 'country' in data:
            fields.append("country = %s")
            values.append(data['country'])
        if 'state' in data:
            fields.append("state = %s")
            values.append(data['state'])
        if 'city' in data:
            fields.append("city = %s")
            values.append(data['city'])
        

        # Ensure we have fields to update
        if not fields:
            raise ValueError("No fields provided to update.")
        
        fields.append("updated_at = NOW()")

        # Append WHERE clause
        query += ", ".join(fields) + " WHERE id = %s"
        values.append(userId)

        # Execute the query
        cursor.execute(query, tuple(values))

    @staticmethod
    def get_all_users(cursor):
        query = "SELECT id, first_name, last_name, email, phone_number FROM users"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_user_by_id(cursor, user_id):
        query = "SELECT id, first_name, last_name, email, phone_number FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
