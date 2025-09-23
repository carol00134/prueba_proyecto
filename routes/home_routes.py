from flask import Blueprint
from controllers.home_controller import HomeController

home_routes = Blueprint('home_routes', __name__)

# Home route
home_routes.add_url_rule('/', 'home', HomeController.home, methods=['GET'])