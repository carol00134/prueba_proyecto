"""
Template helpers para verificar permisos en las plantillas
"""
from flask import session
from utils.auth_utils import can_user_perform_action, get_user_roles

def can_perform_action(module, action):
    """Helper para verificar si el usuario actual puede realizar una acción"""
    if 'usuario' not in session:
        return False
    
    return can_user_perform_action(session['usuario'], module, action)

def is_admin():
    """Verifica si el usuario actual es administrador"""
    user_roles = session.get('user_roles', [])
    return 'administrador' in user_roles

def is_operador():
    """Verifica si el usuario actual es operador"""
    user_roles = session.get('user_roles', [])
    return 'operador' in user_roles

def is_supervisor():
    """Verifica si el usuario actual es supervisor"""
    user_roles = session.get('user_roles', [])
    return 'supervisor' in user_roles

def has_any_role(*roles):
    """Verifica si el usuario tiene alguno de los roles especificados"""
    user_roles = session.get('user_roles', [])
    return any(role in user_roles for role in roles)

def get_current_user_roles():
    """Obtiene los roles del usuario actual"""
    return session.get('user_roles', [])