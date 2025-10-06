from flask import Blueprint
from controllers.puntos_geograficos_controller import PuntosGeograficosController

puntos_geograficos_routes = Blueprint('puntos_geograficos_routes', __name__)


puntos_geograficos_routes.add_url_rule('/puntoGeografico', 'puntoGeografico', PuntosGeograficosController.puntos_geograficos, methods=['GET', 'POST'])
puntos_geograficos_routes.add_url_rule('/puntos_geograficos', 'puntos_geograficos', PuntosGeograficosController.puntos_geograficos, methods=['GET', 'POST'])