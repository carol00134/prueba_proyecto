from flask import render_template, request, session
from werkzeug.security import generate_password_hash
from config import mysql

class UsuariosController:
    @staticmethod
    def usuarios():
        """Handle users management (list, create, edit, delete)"""
        cur = mysql.connection.cursor()
        usuario_editar = None
        error = None
        success = None
        
        if request.method == 'POST':
            accion = request.form.get('accion')
            username = request.form.get('username')
            password = request.form.get('password')
            nombre = request.form.get('nombre')
            rol = request.form.get('rol')
            estado = request.form.get('estado', '1')  # Por defecto activo
            regional = request.form.get('regional', '').strip()  # Campo obligatorio
            activo = bool(int(estado))  # Convertir a boolean
            
            if accion == 'agregar':
                try:
                    # Validación mejorada - campos obligatorios
                    if not username or not username.strip():
                        error = 'El nombre de usuario es obligatorio'
                    elif not password or not password.strip():
                        error = 'La contraseña es obligatoria'
                    elif not nombre or not nombre.strip():
                        error = 'El nombre completo es obligatorio'
                    elif not rol or not rol.strip():
                        error = 'El rol es obligatorio. Debe seleccionar un rol para el usuario.'
                    elif not regional or not regional.strip():
                        error = 'La regional es obligatoria. Debe especificar la regional del usuario.'
                    else:
                        # Verificar que el rol existe antes de crear el usuario
                        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
                        rol_row = cur.fetchone()
                        if not rol_row:
                            error = f'El rol "{rol}" no existe en el sistema'
                        else:
                            # Verificar que el username no existe ya
                            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
                            if cur.fetchone():
                                error = f'El nombre de usuario "{username}" ya existe. Elija uno diferente.'
                            else:
                                # Usar transacción para asegurar consistencia
                                mysql.connection.begin()
                                try:
                                    hashed_password = generate_password_hash(password)
                                    
                                    # Insertar usuario
                                    cur.execute("INSERT INTO usuarios (nombre, usuario, contraseña, activo, regional) VALUES (%s, %s, %s, %s, %s)", 
                                               (nombre, username, hashed_password, activo, regional))
                                    
                                    # Obtener el ID del usuario recién creado
                                    usuario_id = cur.lastrowid
                                    
                                    # Insertar la relación usuario-rol (obligatoria)
                                    rol_id = rol_row['id']
                                    cur.execute("INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)", 
                                               (usuario_id, rol_id))
                                    
                                    # Confirmar transacción
                                    mysql.connection.commit()
                                    success = f'Usuario {username} creado exitosamente con rol {rol}'
                                except Exception as e:
                                    # Revertir cambios si hay error
                                    mysql.connection.rollback()
                                    raise e
                except Exception as e:
                    error = f'Error al crear usuario: {str(e)}'
                    
            elif accion == 'editar':
                try:
                    # Validación mejorada - campos obligatorios
                    if not username or not username.strip():
                        error = 'El nombre de usuario es obligatorio'
                    elif not nombre or not nombre.strip():
                        error = 'El nombre completo es obligatorio'
                    elif not rol or not rol.strip():
                        error = 'El rol es obligatorio. Debe seleccionar un rol para el usuario.'
                    elif not regional or not regional.strip():
                        error = 'La regional es obligatoria. Debe especificar la regional del usuario.'
                    else:
                        # Verificar que el rol existe
                        cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
                        rol_row = cur.fetchone()
                        if not rol_row:
                            error = f'El rol "{rol}" no existe en el sistema'
                        else:
                            # Verificar si el usuario que se está editando es el mismo que está logueado
                            usuario_actual = session.get('usuario')
                            
                            # Verificar si el usuario actual es administrador
                            if usuario_actual == username:
                                cur.execute("""
                                    SELECT r.nombre as rol_nombre 
                                    FROM usuarios u 
                                    JOIN usuario_rol ur ON u.id = ur.usuario_id 
                                    JOIN roles r ON ur.rol_id = r.id 
                                    WHERE u.usuario = %s
                                """, (usuario_actual,))
                                usuario_rol = cur.fetchone()
                                
                                # Si es administrador y está tratando de desactivarse
                                if usuario_rol and usuario_rol['rol_nombre'].lower() == 'administrador' and not activo:
                                    error = 'Error: Como administrador, no puedes desactivar tu propia cuenta. Esto bloquearía el acceso al sistema.'
                                elif usuario_rol and usuario_rol['rol_nombre'].lower() == 'administrador' and rol.lower() != 'administrador':
                                    error = 'Error: Como administrador, no puedes cambiar tu propio rol. Esto bloquearía el acceso al sistema.'
                            
                            # Si no hay errores, proceder con la actualización
                            if not error:
                                # Usar transacción para asegurar consistencia
                                mysql.connection.begin()
                                try:
                                    # Actualizar información del usuario
                                    if password and password.strip():
                                        hashed_password = generate_password_hash(password)
                                        cur.execute("UPDATE usuarios SET nombre = %s, contraseña = %s, activo = %s, regional = %s WHERE usuario = %s", 
                                                   (nombre, hashed_password, activo, regional, username))
                                    else:
                                        cur.execute("UPDATE usuarios SET nombre = %s, activo = %s, regional = %s WHERE usuario = %s", 
                                                   (nombre, activo, regional, username))
                                    
                                    # Obtener el ID del usuario
                                    cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
                                    usuario_row = cur.fetchone()
                                    if usuario_row:
                                        usuario_id = usuario_row['id']
                                        
                                        # Eliminar roles existentes
                                        cur.execute("DELETE FROM usuario_rol WHERE usuario_id = %s", (usuario_id,))
                                        
                                        # Agregar el nuevo rol (obligatorio)
                                        rol_id = rol_row['id']
                                        cur.execute("INSERT INTO usuario_rol (usuario_id, rol_id) VALUES (%s, %s)", 
                                                   (usuario_id, rol_id))
                                    
                                    # Confirmar transacción
                                    mysql.connection.commit()
                                    success = f'Usuario {username} actualizado exitosamente con rol {rol}'
                                    usuario_editar = None
                                except Exception as e:
                                    # Revertir cambios si hay error
                                    mysql.connection.rollback()
                                    raise e
                except Exception as e:
                    error = f'Error al actualizar usuario: {str(e)}'
                    
            elif accion == 'eliminar':
                try:
                    # Verificar si el usuario que se está eliminando es el mismo que está logueado
                    usuario_actual = session.get('usuario')
                    
                    if usuario_actual == username:
                        # Verificar si el usuario actual es administrador
                        cur.execute("""
                            SELECT r.nombre as rol_nombre 
                            FROM usuarios u 
                            JOIN usuario_rol ur ON u.id = ur.usuario_id 
                            JOIN roles r ON ur.rol_id = r.id 
                            WHERE u.usuario = %s
                        """, (usuario_actual,))
                        usuario_rol = cur.fetchone()
                        
                        if usuario_rol and usuario_rol['rol_nombre'].lower() == 'administrador':
                            error = 'Error: Como administrador, no puedes eliminar tu propia cuenta. Esto bloquearía el acceso al sistema.'
                        else:
                            error = 'Error: No puedes eliminar tu propia cuenta mientras estés logueado.'
                    else:
                        # Verificar si el usuario a eliminar es administrador
                        cur.execute("""
                            SELECT r.nombre as rol_nombre 
                            FROM usuarios u 
                            JOIN usuario_rol ur ON u.id = ur.usuario_id 
                            JOIN roles r ON ur.rol_id = r.id 
                            WHERE u.usuario = %s
                        """, (username,))
                        usuario_rol = cur.fetchone()
                        
                        if usuario_rol and usuario_rol['rol_nombre'].lower() == 'administrador':
                            error = 'Error: No se puede eliminar una cuenta de administrador. Cambia el rol primero si es necesario.'
                    
                    # Si no hay errores, proceder con la eliminación
                    if not error:
                        cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (username,))
                        usuario_row = cur.fetchone()
                        if usuario_row:
                            usuario_id = usuario_row['id']
                            cur.execute("DELETE FROM usuario_rol WHERE usuario_id = %s", (usuario_id,))
                            cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
                            mysql.connection.commit()
                            success = f'Usuario {username} eliminado exitosamente'
                except Exception as e:
                    error = f'Error al eliminar usuario: {str(e)}'
                    
            elif accion == 'mostrar_editar':
                cur.execute("""
                    SELECT u.nombre, u.usuario, u.activo, u.regional, r.nombre as rol
                    FROM usuarios u
                    LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
                    LEFT JOIN roles r ON ur.rol_id = r.id
                    WHERE u.usuario = %s
                """, (username,))
                usuario_editar = cur.fetchone()
                
            elif accion == 'cancelar':
                usuario_editar = None
        
        # Obtener lista de usuarios
        cur.execute("""
            SELECT u.nombre, u.usuario, u.activo, u.regional, r.nombre as rol
            FROM usuarios u
            LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
            ORDER BY u.nombre, u.usuario
        """)
        usuarios = cur.fetchall()
        cur.close()
        
        return render_template('usuarios.html', 
                             usuarios=usuarios, 
                             usuario_editar=usuario_editar,
                             error=error,
                             success=success)