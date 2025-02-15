from flask_socketio import SocketIO
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_model import mysql, User

socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")  # Initialize socket
connected_users = {}  # Dictionary to store userId -> socketId mapping

@socketio.on("connect")
@jwt_required()
def handle_connect():
        email = get_jwt_identity()
        cursor = mysql.connection.cursor()
        # Get user details
        user = User.find_by_email(cursor, email)
        if not user:
            return jsonify({"message": "User not found"}), 404
        connected_users[user.id] = request.sid  # Store the user's socket session
        print(f"User {user.id} registered with session {request.sid}")

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
