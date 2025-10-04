from flask import Blueprint
from controllers.mapas_controller import MapasController

mapas_routes = Blueprint('mapas_routes', __name__)

# Maps routes
mapas_routes.add_url_rule('/mapas', 'mapas', MapasController.mapas, methods=['GET'])

# API routes for map data
mapas_routes.add_url_rule('/api/puntos-geograficos', 'get_puntos_geograficos', 
                         MapasController.get_puntos_geograficos, methods=['GET'])
mapas_routes.add_url_rule('/api/camaras', 'get_camaras', 
                         MapasController.get_camaras, methods=['GET'])