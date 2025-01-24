from flask import Blueprint
from controllers.token_controller import refresh_broker_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.token import mysql
from models.user_model import mysql, User

token_routes = Blueprint('token_routes', __name__)

@token_routes.route('/refresh', methods=['GET'])
@jwt_required()
def refresh_token():
    email = get_jwt_identity()
    cursor = mysql.connection.cursor()
    user_data = User.find_by_email(cursor, email)
    response = refresh_broker_token(cursor, user_data)
    mysql.connection.commit()
    cursor.close()
    return response