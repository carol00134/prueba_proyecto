from functools import wraps
from flask import session, request, redirect, url_for, flash, abort
from config import mysql

def login_required(f):
    """Decorador que requiere que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('auth_routes.login'))
        
        # Verificar que los roles estén en la sesión, si no, cargarlos
        if 'user_roles' not in session:
            user_info = get_user_role_info(session['usuario'])
            if user_info:
                session['user_roles'] = user_info['roles_list']
                session['user_id'] = user_info['id']
            else:
                session['user_roles'] = []
                session['user_id'] = None
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorador que requiere que el usuario tenga uno de los roles especificados"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Usar los roles que ya están en la sesión
            user_roles = session.get('user_roles', [])
            
            # Si no hay roles en sesión, intentar cargarlos
            if not user_roles:
                user_roles = get_user_roles(session['usuario'])
                session['user_roles'] = user_roles
            
            # Si el usuario es administrador, puede acceder a todo
            if 'administrador' in user_roles:
                return f(*args, **kwargs)
            
            # Verificar si el usuario tiene alguno de los roles permitidos
            if any(role in user_roles for role in allowed_roles):
                return f(*args, **kwargs)
            
            # Si no tiene permisos, registrar el intento y denegar acceso
            from controllers.bitacora_controller import BitacoraController
            BitacoraController.registrar_accion(
                accion='ACCESS_DENIED',
                modulo='Autorización',
                descripcion=f'Usuario {session["usuario"]} intentó acceder a {request.endpoint} sin permisos. Roles requeridos: {", ".join(allowed_roles)}'
            )
            
            flash('No tienes permisos para acceder a esta sección.', 'error')
            abort(403)
        
        return decorated_function
    return decorator

def get_user_roles(username):
    """Obtiene los roles de un usuario específico"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT r.nombre 
            FROM usuarios u
            JOIN usuario_rol ur ON u.id = ur.usuario_id
            JOIN roles r ON ur.rol_id = r.id
            WHERE u.usuario = %s AND u.activo = TRUE
        """, (username,))
        roles = cur.fetchall()
        cur.close()
        
        return [role['nombre'] for role in roles] if roles else []
    except Exception as e:
        print(f"Error al obtener roles del usuario {username}: {e}")
        return []

def get_user_role_info(username):
    """Obtiene información completa del usuario y sus roles"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.*, GROUP_CONCAT(r.nombre) as roles
            FROM usuarios u
            LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
            WHERE u.usuario = %s AND u.activo = TRUE
            GROUP BY u.id
        """, (username,))
        user_info = cur.fetchone()
        cur.close()
        
        if user_info:
            user_info['roles_list'] = user_info['roles'].split(',') if user_info['roles'] else []
        
        return user_info
    except Exception as e:
        print(f"Error al obtener información del usuario {username}: {e}")
        return None

def get_user_permissions(username, module=None, action=None):
    """Obtiene los permisos específicos de un usuario para módulo/acción"""
    try:
        cur = mysql.connection.cursor()
        
        base_query = """
            SELECT m.nombre as modulo, a.nombre as accion, r.nombre as rol
            FROM usuarios u
            JOIN usuario_rol ur ON u.id = ur.usuario_id
            JOIN roles r ON ur.rol_id = r.id
            JOIN acceso_modulo_accion ama ON r.id = ama.rol_id
            JOIN modulos m ON ama.modulo_id = m.id
            JOIN acciones a ON ama.accion_id = a.id
            WHERE u.usuario = %s AND u.activo = TRUE
        """
        
        params = [username]
        
        if module:
            base_query += " AND m.nombre = %s"
            params.append(module)
            
        if action:
            base_query += " AND a.nombre = %s"
            params.append(action)
        
        cur.execute(base_query, params)
        permissions = cur.fetchall()
        cur.close()
        
        return permissions
    except Exception as e:
        print(f"Error al obtener permisos del usuario {username}: {e}")
        return []

def can_user_perform_action(username, module, action):
    """Verifica si un usuario puede realizar una acción específica en un módulo"""
    user_roles = get_user_roles(username)
    
    # Administrador tiene acceso total excepto eliminar en bitácora
    if 'administrador' in user_roles:
        if module == 'bitacora' and action == 'eliminar':
            return False
        return True
    
    # Definir permisos específicos según tus especificaciones
    permissions = {
        'operador': {
            'tickets': ['ver', 'crear', 'editar'],  # Solo sus propios tickets
            'camaras': ['ver', 'crear'],  # Solo sus propias cámaras
            'mapas': ['ver']
        },
        'supervisor': {
            'usuarios': ['ver'],  # Solo ver lista, no crear
            'camaras': ['ver', 'crear', 'editar'],  # No eliminar
            'puntos_geograficos': ['ver', 'crear', 'editar']  # No eliminar
        }
    }
    
    for role in user_roles:
        if role in permissions:
            module_perms = permissions[role].get(module, [])
            if action in module_perms:
                return True
    
    return False

def is_owner_or_admin(username, table, record_id, owner_field='usuario_creador'):
    """Verifica si el usuario es propietario del registro o administrador"""
    user_roles = get_user_roles(username)
    
    # Administrador puede ver todo
    if 'administrador' in user_roles:
        return True
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"""
            SELECT {owner_field} 
            FROM {table} 
            WHERE id = %s
        """, (record_id,))
        
        result = cur.fetchone()
        cur.close()
        
        if result:
            return result[owner_field] == username
        
        return False
    except Exception as e:
        print(f"Error verificando propietario: {e}")
        return False

def action_required(*required_actions):
    """Decorador que requiere que el usuario tenga permisos para acciones específicas"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # Obtener el módulo desde la ruta o parámetros
            endpoint = request.endpoint if request.endpoint else 'unknown'
            print(f"DEBUG: Endpoint original: {endpoint}")  # Debug
            
            # Mapear endpoints a módulos
            endpoint_to_module = {
                'tickets_routes': 'tickets',
                'camaras_routes': 'camaras', 
                'usuarios_routes': 'usuarios',
                'mapas_routes': 'mapas',
                'puntos_geograficos_routes': 'puntos_geograficos',
                'bitacora': 'bitacora',
                'home_routes': 'home'
            }
            
            module = 'unknown'
            for endpoint_key, module_name in endpoint_to_module.items():
                if endpoint_key in endpoint:
                    module = module_name
                    break
            
            print(f"DEBUG: Módulo detectado: {module}")  # Debug
            print(f"DEBUG: Acciones requeridas: {required_actions}")  # Debug
            
            user_roles = get_user_roles(session['usuario'])
            print(f"DEBUG: Roles del usuario: {user_roles}")  # Debug
            
            # Si es administrador, permitir acceso inmediatamente
            if 'administrador' in user_roles:
                print("DEBUG: Usuario es administrador, acceso permitido")  # Debug
                return f(*args, **kwargs)
            
            # Verificar si tiene alguna de las acciones requeridas
            has_permission = False
            for action in required_actions:
                if can_user_perform_action(session['usuario'], module, action):
                    has_permission = True
                    break
            
            print(f"DEBUG: Tiene permisos: {has_permission}")  # Debug
            
            if not has_permission:
                from controllers.bitacora_controller import BitacoraController
                BitacoraController.registrar_accion(
                    accion='ACCESS_DENIED',
                    modulo='Autorización',
                    descripcion=f'Usuario {session["usuario"]} intentó realizar {"/".join(required_actions)} en {module} sin permisos'
                )
                
                flash(f'No tienes permisos para realizar esta acción en {module}.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator