from flask_socketio import SocketIO , disconnect
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity , decode_token
from models.user_model import mysql, User

socketio = SocketIO(cors_allowed_origins="*")  # Initialize socket
connected_users = {}  # Dictionary to store userId -> socketId mapping

@socketio.on("connect")
def handle_connect():
    """Authenticate user via JWT token in query parameters"""
    token = request.args.get("token")  # Extract token from query string
    if not token:
        print("No token provided, disconnecting")
        disconnect()
        return

    try:
        decoded_token = decode_token(token)
        email = decoded_token["sub"]  # Extract user email from token

        cursor = mysql.connection.cursor()
        user = User.find_by_email(cursor, email)  # Find user in DB
        if not user:
            disconnect()
            return
        
        connected_users[user.id] = request.sid
        print(f"User {user.id} authenticated with session {request.sid}")

    except Exception as e:
        print("Auth failed:", str(e))
        disconnect()


@socketio.on("disconnect")
def handle_disconnect():
    user_id = None
    for uid, sid in connected_users.items():
        if sid == request.sid:
            user_id = uid
            break
    if user_id:
        del connected_users[user_id]  # Remove user from tracking
    print(f"Client {request.sid} disconnected")

@socketio.on("register")
def handle_register(user_id):
    """ When frontend connects, it sends 'register' event with userId. """
    connected_users[user_id] = request.sid  # Store the user's socket session
    print(f"User {user_id} registered with session {request.sid}")

def emit_order_to_user(user_id, order_data):
    """ Emit order details only to the user who placed the order """
    user_socket_id = connected_users.get(user_id)
    print("user_socket_id" , user_socket_id)
    if user_socket_id:
        socketio.emit("Order", order_data, room=user_socket_id)
