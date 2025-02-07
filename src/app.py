from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes.auth_routes import auth_routes
from routes.profile_routes import profile_routes
from routes.broker_credentials_routes import broker_credentials_routes
from routes.settings_routes import settings_routes
from routes.token_routes import token_routes
from models.user_model import init_app
from flask_jwt_extended.exceptions import NoAuthorizationError
import logging
import os
# Request
from utils.httpUtils import HTTP

# Initialize Flask app
app = Flask(__name__)

# Configurations
app.config.from_object('config.Config')

CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize MySQL and Bcrypt
init_app(app)

# Initialize JWT
jwt = JWTManager(app)


http = HTTP()

# Register routes
app.register_blueprint(auth_routes, url_prefix='./tradepi/auth')
app.register_blueprint(profile_routes, url_prefix='/tradepi/user')
app.register_blueprint(broker_credentials_routes, url_prefix='/tradepi/brokercredentials')
app.register_blueprint(settings_routes, url_prefix='/tradepi/settings')
app.register_blueprint(token_routes, url_prefix='/tradepi/broker_token')

@app.errorhandler(NoAuthorizationError)
def handle_no_authorization_error(error):
    return jsonify({"message": "Token is missing or not provided"}), 401

@jwt.unauthorized_loader
def handle_unauthorized_error(err_msg):
    return jsonify({"message": "Authorization error", "error": err_msg}), 401

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return jsonify({"message": "Token has expired"}), 401

@jwt.invalid_token_loader
def handle_invalid_token(err_msg):
    return jsonify({"message": "Invalid token", "error": err_msg}), 401

# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": 'Not Found', "error": str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"message": 'Bad Request', "error": str(error)}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": 'Internal Server Error', "error": str(error)}), 500

# Global error handler for SQL exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    response = {
        'message': 'An unexpected error occurred.',
        'error': str(error)
    }
    return jsonify(response), 500

# Route for root URL
@app.route('/tradepi')
def welcome():
    return jsonify({"message": "Welcome to TradePi"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)