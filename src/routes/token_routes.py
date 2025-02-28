from flask import Blueprint, request, jsonify
from controllers.token import refresh_broker_token, create_upstox_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.token import mysql
from models.user_model import mysql, User

token_routes = Blueprint('token_routes', __name__)

@token_routes.route('/refresh', methods=['GET'])
@jwt_required()
def refresh_token():
    email = get_jwt_identity()
    cursor = mysql.connection.cursor()
    user = User.get_user_by_email(cursor, email)
    response = refresh_broker_token(cursor, user)
    mysql.connection.commit()
    cursor.close()
    return response

@token_routes.route('/create-upstox', methods=['POST'])
@jwt_required()
def create_upstox():
    data = request.get_json()
    email = get_jwt_identity()
    cursor = mysql.connection.cursor()
    user = User.get_user_by_email(cursor, email)
    data['userId'] = user.get('id')
    data['client_code'] = data.get('interactiveUserId')
    
    response = create_upstox_token(cursor, data)
    mysql.connection.commit()
    cursor.close()
    return response