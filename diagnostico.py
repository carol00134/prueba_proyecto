"""
Script de diagnóstico para verificar el sistema de roles
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("1. Verificando importación de Flask...")
    from flask import Flask
    print("✓ Flask importado correctamente")
    
    print("2. Verificando importación de config...")
    import config
    print("✓ Config importado correctamente")
    
    print("3. Verificando importación de auth_utils...")
    from utils.auth_utils import get_user_roles, can_user_perform_action
    print("✓ auth_utils importado correctamente")
    
    print("4. Verificando importación de template_helpers...")
    from utils.template_helpers import can_perform_action
    print("✓ template_helpers importado correctamente")
    
    print("5. Verificando controladores...")
    from controllers.auth_controller import AuthController
    from controllers.tickets_controller import TicketsController
    print("✓ Controladores importados correctamente")
    
    print("6. Verificando rutas...")
    from routes.auth_routes import auth_routes
    from routes.tickets_routes import tickets_routes
    print("✓ Rutas importadas correctamente")
    
    print("\n🎉 Todas las importaciones son exitosas!")
    print("El problema puede estar en:")
    print("- Conexión a la base de datos")
    print("- Permisos no configurados en la BD")
    print("- Error específico al procesar una página")
    
except Exception as e:
    print(f"❌ Error encontrado: {e}")
    import traceback
    traceback.print_exc()