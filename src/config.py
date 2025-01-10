import logging
import os

class Config:
    # Database configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'your_db_name')

    # Secret key for JWT
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

    # Setup logging configuration
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    @staticmethod
    def init_app(app):
        # Configure logging
        logging.basicConfig(
            level=Config.LOGGING_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(Config.LOG_FILE), logging.StreamHandler()]
        )
