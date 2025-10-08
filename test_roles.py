"""
Script de prueba para verificar el sistema de control de acceso por roles
"""

from utils.auth_utils import get_user_roles, get_user_role_info, check_module_access

def test_role_system():
    """Función para probar el sistema de roles"""
    print("=== TESTING ROLE-BASED ACCESS CONTROL SYSTEM ===\n")
    
    # Lista de usuarios de prueba (debes tener estos usuarios en tu BD)
    test_users = ['admin_user', 'operador_user', 'supervisor_user']
    
    # Lista de módulos a probar
    modules = ['tickets', 'camaras', 'mapas', 'usuarios', 'puntos_geograficos', 'bitacora', 'home']
    
    for username in test_users:
        print(f"--- Testing user: {username} ---")
        
        # Obtener roles del usuario
        user_roles = get_user_roles(username)
        print(f"Roles: {user_roles}")
        
        # Obtener información completa del usuario
        user_info = get_user_role_info(username)
        if user_info:
            print(f"User ID: {user_info['id']}, Roles: {user_info.get('roles_list', [])}")
        else:
            print("Usuario no encontrado o inactivo")
            continue
        
        # Probar acceso a cada módulo
        print("Module access permissions:")
        for module in modules:
            has_access = check_module_access(username, module)
            status = "✓ ALLOWED" if has_access else "✗ DENIED"
            print(f"  {module}: {status}")
        
        print()

def show_expected_permissions():
    """Muestra los permisos esperados por rol"""
    print("=== EXPECTED PERMISSIONS BY ROLE ===\n")
    
    permissions = {
        'administrador': ['tickets', 'camaras', 'mapas', 'usuarios', 'puntos_geograficos', 'bitacora', 'home'],
        'operador': ['tickets', 'camaras', 'mapas'],
        'supervisor': ['camaras', 'usuarios', 'puntos_geograficos']
    }
    
    for role, modules in permissions.items():
        print(f"--- {role.upper()} ---")
        print(f"Access to: {', '.join(modules)}")
        print()
        
    print("NAVIGATION BEHAVIOR:")
    print("- Administrador: Acceso al dashboard completo")
    print("- Operador: Redirigido a tickets al entrar")
    print("- Supervisor: Redirigido a usuarios al entrar")
    print()

if __name__ == "__main__":
    show_expected_permissions()
    test_role_system()