from flask import Flask, request, jsonify
import re
from utils.send_email import send_email
import random
import string
from datetime import datetime, timedelta
from models.user_model import User

def format_query_result(rows, column_names):
    """
    Transforms query result rows into a list of dictionaries based on column names.
    :param rows: List of tuples (query results).
    :param column_names: List of column names corresponding to the rows.
    :return: List of dictionaries representing the query result.
    """
    return [dict(zip(column_names, row)) for row in rows]

def format_single_query_result(row, column_names):
    """
    Transforms a single query result row into a dictionary based on column names.
    :param row: A tuple representing a single row (query result).
    :param column_names: List of column names corresponding to the row.
    :return: A dictionary representing the single query result.
    """
    if row is not None:
        return dict(zip(column_names, row))
    return None

def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Must contain at least one uppercase letter.")
    if not re.search(r"\d", password):
        errors.append("Must contain at least one number.")
    if not re.search(r"[@$!%*?&]", password):
        errors.append("Must contain at least one special character.")
    return errors

def verify_otp(cursor, email, otp):
    cursor.execute("SELECT otp, otp_expiration FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()  # Fetch the result as a tuple (otp, otp_expiration)
    print(user)
    if not user:
        return False
    stored_otp, otp_expiration = user
    # Check if OTP exists and has not expired
    if not stored_otp or otp_expiration < datetime.utcnow():
        return False

    if otp == stored_otp:
        # OTP is verified, now remove it from the database
        cursor.execute("UPDATE users SET otp = NULL, otp_expiration = NULL WHERE email = %s", (email,))
        return True

    return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(cursor, email):
    """Send OTP to the user's email and store it in the database."""
    try:
        otp = generate_otp()
        otp_expiration = datetime.utcnow() + timedelta(minutes=5)

        # Send OTP via email
        email_sent = send_email(
            subject="Your OTP Code",
            recipient=email,
            body=f"Your OTP is {otp}. It is valid for 5 minutes."
        )

        if not email_sent:
            return jsonify({"message": "Failed to send OTP. Try again later."}), 500

        # Store OTP and expiration in the database
        query = """
            UPDATE users 
            SET otp = %s, otp_expiration = %s 
            WHERE email = %s
        """
        cursor.execute(query, (otp, otp_expiration, email))

        return jsonify({"message": "OTP sent to your email. Please verify."}), 200

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500    