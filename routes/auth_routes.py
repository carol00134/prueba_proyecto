from flask import Blueprint
from controllers.auth_controller import AuthController

auth_routes = Blueprint('auth_routes', __name__)

# Authentication routes
auth_routes.add_url_rule('/login', 'login', AuthController.login, methods=['GET', 'POST'])
auth_routes.add_url_rule('/register', 'register', AuthController.register, methods=['GET', 'POST'])
auth_routes.add_url_rule('/logout', 'logout', AuthController.logout, methods=['GET'])