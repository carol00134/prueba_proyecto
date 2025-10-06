from flask import Flask
import pymysql

# Configure PyMySQL to work as MySQLdb replacement
pymysql.install_as_MySQLdb()

# Database configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'proyecto',
    'charset': 'utf8mb4',
    'autocommit': True
}

class DatabaseConnection:
    """Wrapper class to mimic Flask-MySQLdb behavior"""
    def __init__(self):
        self._connection = None
    
    @property
    def connection(self):
        """Get database connection that returns DictCursor by default"""
        if self._connection is None or not self._connection.open:
            try:
                # Configure connection to use DictCursor by default
                config = MYSQL_CONFIG.copy()
                self._connection = pymysql.connect(**config)
                # Patch the cursor method to always return DictCursor
                original_cursor = self._connection.cursor
                self._connection.cursor = lambda: original_cursor(pymysql.cursors.DictCursor)
            except Exception as e:
                print(f"Error connecting to database: {e}")
                return None
        return self._connection
    
    def cursor(self):
        """Get cursor from connection"""
        if self.connection:
            return self.connection.cursor()
        return None

# Create global mysql instance for backward compatibility
mysql = DatabaseConnection()

def get_db_connection():
    """Get database connection using PyMySQL"""
    try:
        connection = pymysql.connect(**MYSQL_CONFIG)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_app(app):
    """Initialize the app with configuration"""
    # Set secret key
    app.secret_key = '1234'
    
    # Store database config in app config for reference
    app.config['DATABASE'] = MYSQL_CONFIG
    
    return app