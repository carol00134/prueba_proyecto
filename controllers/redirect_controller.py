from flask import redirect, url_for, session
from utils.auth_utils import login_required

class RedirectController:
    @staticmethod
    @login_required
    def index():
        """Redirige a los usuarios según su rol"""
        user_roles = session.get('user_roles', [])
        
        # Administrador va al home (dashboard)
        if 'administrador' in user_roles:
            return redirect(url_for('home_routes.home'))
        
        # Operador va a tickets (su primer módulo)
        elif 'operador' in user_roles:
            return redirect(url_for('tickets_routes.tickets'))
        
        # Supervisor va a usuarios (su primer módulo)
        elif 'supervisor' in user_roles:
            return redirect(url_for('usuarios_routes.usuarios'))
        
        # Si no tiene roles específicos, ir al login
        else:
            return redirect(url_for('auth_routes.login'))