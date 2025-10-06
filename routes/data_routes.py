from flask import Blueprint
from controllers.data_controller import DataController

data_routes = Blueprint('data_routes', __name__)


data_routes.add_url_rule('/poblar_datos', 'poblar_datos', DataController.poblar_datos, methods=['GET'])