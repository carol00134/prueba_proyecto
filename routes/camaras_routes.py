from flask import Blueprint
from controllers.camaras_controller import CamarasController
from controllers.excel_controller import ExcelController

camaras_routes = Blueprint('camaras_routes', __name__)

camaras_routes.add_url_rule('/camaras', 'camaras', CamarasController.camaras, methods=['GET', 'POST'])

camaras_routes.add_url_rule('/api/camara/<id_camara>', 'get_camara', CamarasController.get_camara, methods=['GET'])

# Rutas para importación de Excel
camaras_routes.add_url_rule('/camaras/importar-excel', 'importar_camaras_excel', ExcelController.importar_camaras, methods=['POST'])
camaras_routes.add_url_rule('/camaras/exportar-excel', 'exportar_camaras_excel', ExcelController.exportar_camaras, methods=['GET'])