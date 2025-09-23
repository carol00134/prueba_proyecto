from flask import Blueprint
from controllers.usuarios_controller import UsuariosController

usuarios_routes = Blueprint('usuarios_routes', __name__)

# Users management routes
usuarios_routes.add_url_rule('/usuarios', 'usuarios', UsuariosController.usuarios, methods=['GET', 'POST'])