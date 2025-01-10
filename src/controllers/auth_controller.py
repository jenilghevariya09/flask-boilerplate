from flask import jsonify
from models.user_model import User
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import SQLAlchemyError
from utils.auth_helpers import create_jwt_token

bcrypt = Bcrypt()

def register_user(cursor, username, password):
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        return jsonify({"message": "User registered successfully"}), 201
    except SQLAlchemyError as e:
        return jsonify({"message": "Database error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred while registering the user", "error": str(e)}), 500

def login_user(cursor, username, password):
    try:
        user = User.find_by_username(cursor, username)
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_jwt_token(identity=user.username)
            return jsonify({"access_token": access_token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred during login", "error": str(e)}), 500
