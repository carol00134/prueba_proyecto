from flask import render_template, request, jsonify, session
from config import mysql

class CamarasController:
    @staticmethod
    def camaras():
        """Handle cameras management"""
        error = None
        success = None
        
        if request.method == 'POST':
            accion = request.form.get('accion')
            print(f"DEBUG: Acción recibida: '{accion}'")  # Log para debug
            
            cur = mysql.connection.cursor()
            
            try:
                if accion == 'agregar':
                    # Obtener datos del formulario
                    id_camaras = request.form.get('id_camaras', '').strip()
                    correo = request.form.get('correo', '').strip()
                    nombre = request.form.get('nombre', '').strip()
                    estado = request.form.get('estado')
                    regional = request.form.get('regional', '').strip()
                    fecha_creacion = request.form.get('fecha_creacion')
                    fecha_ultima_modificacion = request.form.get('fecha_ultima_modificacion')
                    cambio_password = request.form.get('cambio_password')
                    usuario_id = request.form.get('usuario_id') if request.form.get('usuario_id') else None
                    rol_id = request.form.get('rol_id') if request.form.get('rol_id') else None
                    
                    print(f"DEBUG: Agregando cámara con ID: '{id_camaras}'")  # Log para debug
                    
                    # Validar campos obligatorios
                    if not id_camaras:
                        error = 'El ID de la cámara es obligatorio'
                    elif not correo:
                        error = 'El correo electrónico es obligatorio'
                    elif not nombre:
                        error = 'El nombre es obligatorio'
                    else:
                        # Verificar si el ID ya existe
                        cur.execute("SELECT COUNT(*) as count FROM camaras WHERE id_camaras = %s", (id_camaras,))
                        result = cur.fetchone()
                        if result['count'] > 0:
                            error = f'Ya existe una cámara con el ID "{id_camaras}"'
                        else:
                            # Insertar nueva cámara
                            cur.execute("""
                                INSERT INTO camaras (id_camaras, correo, nombre, estado, regional, 
                                                   fecha_creacion, fecha_ultima_modificacion, cambio_password, 
                                                   usuario_id, rol_id) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (id_camaras, correo, nombre, estado, 
                                 regional if regional else None,
                                 fecha_creacion if fecha_creacion else None,
                                 fecha_ultima_modificacion if fecha_ultima_modificacion else None,
                                 cambio_password if cambio_password else None,
                                 usuario_id, rol_id))
                            
                            mysql.connection.commit()
                            success = f'Cámara "{nombre}" agregada exitosamente'
                    
                elif accion == 'eliminar':
                    id_camaras = request.form.get('id_camaras')
                    cur.execute("DELETE FROM camaras WHERE id_camaras = %s", (id_camaras,))
                    mysql.connection.commit()
                    success = 'Cámara eliminada exitosamente'
                
                elif accion == 'editar':
                    # Obtener datos del formulario para editar
                    id_camaras = request.form.get('id_camaras', '').strip()
                    id_camaras_original = request.form.get('id_camaras_original', '').strip()  # ID original antes de la edición
                    correo = request.form.get('correo', '').strip()
                    nombre = request.form.get('nombre', '').strip()
                    estado = request.form.get('estado')
                    regional = request.form.get('regional', '').strip()
                    fecha_creacion = request.form.get('fecha_creacion')
                    fecha_ultima_modificacion = request.form.get('fecha_ultima_modificacion')
                    cambio_password = request.form.get('cambio_password')
                    usuario_id = request.form.get('usuario_id') if request.form.get('usuario_id') else None
                    rol_id = request.form.get('rol_id') if request.form.get('rol_id') else None
                    
                    print(f"DEBUG: Editando cámara. ID original: '{id_camaras_original}', ID nuevo: '{id_camaras}'")  # Log para debug
                    
                    # Validar campos obligatorios
                    if not id_camaras:
                        error = 'El ID de la cámara es obligatorio'
                    elif not correo:
                        error = 'El correo electrónico es obligatorio'
                    elif not nombre:
                        error = 'El nombre es obligatorio'
                    else:
                        # Si el ID cambió, verificar que el nuevo ID no exista en otra cámara
                        if id_camaras != id_camaras_original:
                            cur.execute("SELECT COUNT(*) as count FROM camaras WHERE id_camaras = %s", (id_camaras,))
                            result = cur.fetchone()
                            if result['count'] > 0:
                                error = f'Ya existe una cámara con el ID "{id_camaras}"'
                        
                        if not error:
                            # Actualizar cámara existente usando el ID original
                            cur.execute("""
                                UPDATE camaras SET 
                                    id_camaras = %s, correo = %s, nombre = %s, estado = %s, regional = %s,
                                    fecha_creacion = %s, fecha_ultima_modificacion = %s, 
                                    cambio_password = %s, usuario_id = %s, rol_id = %s
                                WHERE id_camaras = %s
                            """, (id_camaras, correo, nombre, estado, 
                                 regional if regional else None,
                                 fecha_creacion if fecha_creacion else None,
                                 fecha_ultima_modificacion if fecha_ultima_modificacion else None,
                                 cambio_password if cambio_password else None,
                                 usuario_id, rol_id, id_camaras_original))
                            
                            mysql.connection.commit()
                            success = f'Cámara "{nombre}" actualizada exitosamente'
                    
                    # Si es una petición AJAX para editar, retornar JSON
                    if accion == 'editar':
                        if error:
                            return jsonify({'success': False, 'message': error})
                        else:
                            return jsonify({'success': True, 'message': success})
                    
            except Exception as e:
                error = f'Error: {str(e)}'
                # Si es una petición AJAX para editar y hay error, retornar JSON
                if request.form.get('accion') == 'editar':
                    return jsonify({'success': False, 'message': error})
            finally:
                cur.close()
        
        # Obtener datos para mostrar
        cur = mysql.connection.cursor()
        
        # Obtener cámaras con información de usuario y rol
        cur.execute("""
            SELECT c.id_camaras, c.correo, c.nombre, c.estado, c.regional,
                   c.fecha_creacion, c.fecha_ultima_modificacion, c.cambio_password,
                   c.usuario_id, c.rol_id,
                   u.nombre as usuario_nombre, r.nombre as rol_nombre
            FROM camaras c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            LEFT JOIN roles r ON c.rol_id = r.id
            ORDER BY c.nombre
        """)
        camaras = cur.fetchall()
        
        # Obtener información del usuario logueado
        usuario_logueado = session.get('usuario')
        usuario_actual = None
        if usuario_logueado:
            cur.execute("""
                SELECT u.id, u.nombre, u.usuario, r.nombre as rol
                FROM usuarios u
                LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
                LEFT JOIN roles r ON ur.rol_id = r.id
                WHERE u.usuario = %s
            """, (usuario_logueado,))
            usuario_actual = cur.fetchone()
        
        # Obtener usuarios para el dropdown
        cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
        usuarios = cur.fetchall()
        
        # Obtener roles para el dropdown
        cur.execute("SELECT id, nombre FROM roles ORDER BY nombre")
        roles = cur.fetchall()
        
        cur.close()
        
        return render_template('camaras.html',
                             camaras=camaras,
                             usuarios=usuarios,
                             usuario_actual=usuario_actual,
                             roles=roles,
                             error=error,
                             success=success)