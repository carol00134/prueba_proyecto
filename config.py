from flask import Flask
from flask_mysqldb import MySQL

# Database configuration
MYSQL_CONFIG = {
    'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': '',
    'MYSQL_DB': 'proyecto',
    'MYSQL_CURSORCLASS': 'DictCursor'
}

# Initialize MySQL
mysql = MySQL()

def init_app(app):
    """Initialize the app with configuration"""
    # Apply MySQL configuration
    for key, value in MYSQL_CONFIG.items():
        app.config[key] = value
    
    # Initialize MySQL with app
    mysql.init_app(app)
    
    # Set secret key
    app.secret_key = '1234'
    
    return app