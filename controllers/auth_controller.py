from flask import render_template, redirect, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import mysql

class AuthController:
    @staticmethod
    def login():
        """Handle user login"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template('login.html', error='Por favor complete todos los campos')
            
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT u.*
                FROM usuarios u
                WHERE u.usuario = %s
            """, (username,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                if check_password_hash(user['contraseña'], password):
                    session['usuario'] = username
                    
                    # Obtener roles del usuario y almacenar en sesión
                    from utils.auth_utils import get_user_role_info
                    user_info = get_user_role_info(username)
                    if user_info:
                        session['user_roles'] = user_info['roles_list']
                        session['user_id'] = user_info['id']
                    else:
                        session['user_roles'] = []
                        session['user_id'] = None
                    
                    # Registrar login en bitácora
                    from controllers.bitacora_controller import BitacoraController
                    BitacoraController.registrar_accion(
                        accion='LOGIN',
                        modulo='Autenticación',
                        descripcion=f'Usuario {username} inició sesión exitosamente con roles: {", ".join(session.get("user_roles", []))}'
                    )
                    
                    return redirect('/')
                else:
                    # Registrar intento fallido en bitácora
                    from controllers.bitacora_controller import BitacoraController
                    BitacoraController.registrar_accion(
                        accion='LOGIN_FAILED',
                        modulo='Autenticación',
                        descripcion=f'Intento de login fallido para usuario {username} - Contraseña incorrecta'
                    )
                    return render_template('login.html', error='Contraseña incorrecta')
            else:
                # Registrar intento fallido en bitácora
                from controllers.bitacora_controller import BitacoraController
                BitacoraController.registrar_accion(
                    accion='LOGIN_FAILED',
                    modulo='Autenticación',
                    descripcion=f'Intento de login fallido - Usuario {username} no encontrado'
                )
                return render_template('login.html', error='Usuario no encontrado')
        return render_template('login.html')

    @staticmethod
    def register():
        """Handle user registration"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            hashed_password = generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            return redirect('/login')
        return render_template('login.html')

    @staticmethod
    def logout():
        """Handle user logout"""
        # Registrar logout en bitácora antes de cerrar sesión
        if 'usuario' in session:
            from controllers.bitacora_controller import BitacoraController
            BitacoraController.registrar_accion(
                accion='LOGOUT',
                modulo='Autenticación',
                descripcion=f'Usuario {session["usuario"]} cerró sesión'
            )
        
        # Limpiar toda la información de la sesión
        session.pop('usuario', None)
        session.pop('user_roles', None)
        session.pop('user_id', None)
        return redirect('/login')