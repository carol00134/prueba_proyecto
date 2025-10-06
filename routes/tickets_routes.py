from flask import Blueprint
from controllers.tickets_controller import TicketsController

tickets_routes = Blueprint('tickets_routes', __name__)


tickets_routes.add_url_rule('/agregar_ticket', 'agregar_ticket', TicketsController.agregar_ticket, methods=['GET'])
tickets_routes.add_url_rule('/editar_ticket/<ticket_id>', 'editar_ticket', TicketsController.editar_ticket, methods=['GET'])
tickets_routes.add_url_rule('/ticket/<ticket_id>', 'detalle_ticket', TicketsController.detalle_ticket, methods=['GET'])
tickets_routes.add_url_rule('/tickets', 'tickets', TicketsController.tickets, methods=['GET', 'POST'])
tickets_routes.add_url_rule('/api/ticket/<ticket_id>', 'api_ticket_detalles', TicketsController.api_ticket_detalles, methods=['GET'])