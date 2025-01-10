from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes.auth_routes import auth_routes
from routes.profile_routes import profile_routes
from routes.xts_auth_routes import xts_auth_routes
from routes.settings_routes import settings_routes
from models.user_model import init_app
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
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(profile_routes, url_prefix='/user')
app.register_blueprint(xts_auth_routes, url_prefix='/xts')
app.register_blueprint(settings_routes, url_prefix='/settings')

# Error handling
@app.errorhandler(404)
def not_found(error):
    return http.response([], 404)

@app.errorhandler(400)
def bad_request(error):
    return http.response([], 400)

@app.errorhandler(500)
def internal_error(error):
    return http.response([], 500)

# Global error handler for SQL exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    response = {
        'message': 'An unexpected error occurred.',
        'error': str(error)
    }
    return jsonify(response), 500

    # Check if the database is connected

if __name__ == '__main__':
    app.run(debug=True)
