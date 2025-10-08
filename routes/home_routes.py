from flask import Blueprint
from controllers.home_controller import HomeController
from controllers.redirect_controller import RedirectController

home_routes = Blueprint('home_routes', __name__)

# Root redirect route
home_routes.add_url_rule('/', 'index', RedirectController.index, methods=['GET'])

# Admin dashboard route
home_routes.add_url_rule('/home', 'home', HomeController.home, methods=['GET'])