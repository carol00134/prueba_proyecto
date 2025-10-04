from flask import Blueprint
from controllers.camaras_controller import CamarasController

camaras_routes = Blueprint('camaras_routes', __name__)

# Cameras management routes
camaras_routes.add_url_rule('/camaras', 'camaras', CamarasController.camaras, methods=['GET', 'POST'])

# API route for individual camera data
camaras_routes.add_url_rule('/api/camara/<id_camara>', 'get_camara', CamarasController.get_camara, methods=['GET'])