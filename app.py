from flask import Flask, render_template, session
import config

# Import all route blueprints
from routes.home_routes import home_routes
from routes.auth_routes import auth_routes
from routes.usuarios_routes import usuarios_routes
from routes.mapas_routes import mapas_routes
from routes.puntos_Geograficos import puntos_geograficos_routes
from routes.camaras_routes import camaras_routes
from routes.tickets_routes import tickets_routes
from routes.api_routes import api_routes
from routes.data_routes import data_routes
from routes.bitacora_routes import bitacora_routes

# Create Flask app
app = Flask(__name__, template_folder='template')

# Initialize configuration
config.init_app(app)

# Error handlers for unauthorized access
@app.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors (access denied)"""
    return render_template('error_403.html'), 403

# Make user roles available in all templates
@app.context_processor
def inject_user_roles():
    """Make user roles available in all templates"""
    from utils.template_helpers import (
        can_perform_action, is_admin, is_operador, is_supervisor, 
        has_any_role, get_current_user_roles
    )
    
    user_roles = session.get('user_roles', [])
    return dict(
        user_roles=user_roles,
        can_perform_action=can_perform_action,
        is_admin=is_admin,
        is_operador=is_operador,
        is_supervisor=is_supervisor,
        has_any_role=has_any_role,
        get_current_user_roles=get_current_user_roles
    )

# Register all blueprints
app.register_blueprint(home_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(usuarios_routes)
app.register_blueprint(mapas_routes)
app.register_blueprint(puntos_geograficos_routes)
app.register_blueprint(camaras_routes)
app.register_blueprint(tickets_routes)
app.register_blueprint(api_routes)
app.register_blueprint(data_routes)
app.register_blueprint(bitacora_routes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

