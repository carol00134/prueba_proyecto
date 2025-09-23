from flask import Blueprint
from controllers.api_controller import ApiController

api_routes = Blueprint('api_routes', __name__)

# API routes
api_routes.add_url_rule('/api/puntos', 'api_puntos', ApiController.api_puntos, methods=['GET'])
api_routes.add_url_rule('/api/usuarios_activos', 'api_usuarios_activos', ApiController.api_usuarios_activos, methods=['GET'])
api_routes.add_url_rule('/api/municipios/<int:departamento_id>', 'api_municipios', ApiController.api_municipios, methods=['GET'])
api_routes.add_url_rule('/api/subtipologias/<int:tipologia_id>', 'api_subtipologias', ApiController.api_subtipologias, methods=['GET'])
api_routes.add_url_rule('/api/camara/<id_camaras>', 'api_camara_detalles', ApiController.api_camara_detalles, methods=['GET'])