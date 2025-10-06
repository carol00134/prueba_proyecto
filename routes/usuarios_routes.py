from flask import Blueprint
from controllers.usuarios_controller import UsuariosController

usuarios_routes = Blueprint('usuarios_routes', __name__)


usuarios_routes.add_url_rule('/usuarios', 'usuarios', UsuariosController.usuarios, methods=['GET', 'POST'])