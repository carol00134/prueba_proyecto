from flask import Blueprint
from controllers.bitacora_controller import BitacoraController

bitacora_routes = Blueprint('bitacora', __name__)

@bitacora_routes.route('/bitacora')
def bitacora_index():
    """Página principal de bitácora"""
    return BitacoraController.index()

@bitacora_routes.route('/bitacora/detalle/<int:id>')
def bitacora_detalle(id):
    """Obtener detalle de un registro específico"""
    return BitacoraController.get_detalle(id)
