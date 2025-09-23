from flask import Blueprint
from controllers.mapas_controller import MapasController

mapas_routes = Blueprint('mapas_routes', __name__)

# Maps routes
mapas_routes.add_url_rule('/mapas', 'mapas', MapasController.mapas, methods=['GET'])