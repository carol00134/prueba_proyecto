"""
Decorador para automatizar el registro de actividades en bitácora
"""
from functools import wraps
from flask import session, request
from controllers.bitacora_controller import BitacoraController
import json

def registrar_bitacora(accion, modulo, descripcion_template=None):
    """
    Decorador para registrar automáticamente las acciones en bitácora
    
    Args:
        accion (str): Tipo de acción (CREATE, UPDATE, DELETE, VIEW, etc.)
        modulo (str): Módulo donde se realiza la acción
        descripcion_template (str): Template de descripción con placeholders
    
    Ejemplo de uso:
        @registrar_bitacora('CREATE', 'Usuarios', 'Creó el usuario {usuario}')
        def crear_usuario():
            # ... lógica del método
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Ejecutar la función original
            resultado = func(*args, **kwargs)
            
            # Solo registrar si hay usuario logueado
            if 'usuario' in session:
                try:
                    # Generar descripción automática
                    if descripcion_template:
                        # Obtener datos del formulario para la descripción
                        form_data = request.form.to_dict() if request.form else {}
                        descripcion = descripcion_template.format(**form_data, **kwargs)
                    else:
                        descripcion = f'Ejecutó {func.__name__} en módulo {modulo}'
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion=accion,
                        modulo=modulo,
                        descripcion=descripcion
                    )
                except Exception as e:
                    # Si hay error en bitácora, no afectar la función principal
                    print(f"Error al registrar en bitácora: {e}")
            
            return resultado
        return wrapper
    return decorator

def registrar_cambios_bitacora(accion, modulo, obtener_datos_anteriores=None):
    """
    Decorador avanzado para registrar cambios con datos anteriores y nuevos
    
    Args:
        accion (str): Tipo de acción
        modulo (str): Módulo donde se realiza la acción
        obtener_datos_anteriores (function): Función para obtener datos anteriores
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            datos_anteriores = None
            
            # Obtener datos anteriores si se proporciona la función
            if obtener_datos_anteriores and 'usuario' in session:
                try:
                    datos_anteriores = obtener_datos_anteriores(*args, **kwargs)
                except Exception as e:
                    print(f"Error al obtener datos anteriores: {e}")
            
            # Ejecutar la función original
            resultado = func(*args, **kwargs)
            
            # Registrar en bitácora si hay usuario logueado
            if 'usuario' in session:
                try:
                    # Obtener datos nuevos del formulario
                    datos_nuevos = request.form.to_dict() if request.form else None
                    
                    # Generar descripción
                    descripcion = f'Realizó {accion.lower()} en {modulo}'
                    if request.form and 'nombre' in request.form:
                        descripcion += f' - {request.form["nombre"]}'
                    
                    BitacoraController.registrar_accion(
                        accion=accion,
                        modulo=modulo,
                        descripcion=descripcion,
                        datos_anteriores=datos_anteriores,
                        datos_nuevos=datos_nuevos
                    )
                except Exception as e:
                    print(f"Error al registrar cambios en bitácora: {e}")
            
            return resultado
        return wrapper
    return decorator

# Funciones auxiliares para obtener datos anteriores comunes
def obtener_usuario_anterior(user_id):
    """Obtener datos anteriores de un usuario"""
    from config import mysql
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        usuario = cur.fetchone()
        cur.close()
        return dict(usuario) if usuario else None
    except:
        return None

def obtener_ticket_anterior(ticket_id):
    """Obtener datos anteriores de un ticket"""
    from config import mysql
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
        ticket = cur.fetchone()
        cur.close()
        return dict(ticket) if ticket else None
    except:
        return None

def obtener_camara_anterior(camara_id):
    """Obtener datos anteriores de una cámara"""
    from config import mysql
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM camaras WHERE id = %s", (camara_id,))
        camara = cur.fetchone()
        cur.close()
        return dict(camara) if camara else None
    except:
        return None