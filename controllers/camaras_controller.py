from flask import render_template, request, jsonify, session
from config import mysql
from controllers.bitacora_controller import BitacoraController

class CamarasController:
    @staticmethod
    def get_camara(id_camara):
        """Get individual camera data for API"""
        try:
            cur = mysql.connection.cursor()
            
            cur.execute("""
                SELECT id_camaras, correo, nombre, estado, regional,
                       fecha_creacion, fecha_ultima_modificacion, cambio_password,
                       usuario_id, latitud, longitud
                FROM camaras 
                WHERE id_camaras = %s
            """, (id_camara,))
            
            camara = cur.fetchone()
            cur.close()
            
            if camara:
                # Convertir fecha a string si existe
                if camara.get('fecha_creacion'):
                    camara['fecha_creacion'] = camara['fecha_creacion'].strftime('%Y-%m-%d')
                
                return jsonify({
                    'success': True,
                    'camara': camara
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Cámara no encontrada'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al obtener la cámara: {str(e)}'
            })

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
                    latitud = request.form.get('latitud', '').strip()
                    longitud = request.form.get('longitud', '').strip()
                    
                    print(f"DEBUG: Agregando cámara con ID: '{id_camaras}'")  # Log para debug
                    
                    # Validar campos obligatorios
                    if not id_camaras:
                        error = 'El ID de la cámara es obligatorio'
                    elif not correo:
                        error = 'El correo electrónico es obligatorio'
                    elif not nombre:
                        error = 'El nombre es obligatorio'
                    else:
                        # Validar coordenadas si se proporcionan
                        latitud_val = None
                        longitud_val = None
                        if latitud and longitud:
                            try:
                                latitud_val = float(latitud)
                                longitud_val = float(longitud)
                                if not (-90 <= latitud_val <= 90):
                                    error = 'La latitud debe estar entre -90 y 90 grados'
                                elif not (-180 <= longitud_val <= 180):
                                    error = 'La longitud debe estar entre -180 y 180 grados'
                            except ValueError:
                                error = 'Las coordenadas deben ser números válidos'
                        elif latitud or longitud:
                            error = 'Debe proporcionar tanto latitud como longitud, o dejar ambos campos vacíos'
                        
                        if not error:
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
                                                       usuario_id, latitud, longitud) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """, (id_camaras, correo, nombre, estado, 
                                     regional if regional else None,
                                     fecha_creacion if fecha_creacion else None,
                                     fecha_ultima_modificacion if fecha_ultima_modificacion else None,
                                     cambio_password if cambio_password else None,
                                     usuario_id, latitud_val, longitud_val))
                                
                                mysql.connection.commit()
                                success = f'Cámara "{nombre}" agregada exitosamente'
                                
                                # Registrar en bitácora
                                BitacoraController.registrar_accion(
                                    accion='CREATE',
                                    modulo='Cámaras',
                                    descripcion=f'Creó la cámara {id_camaras} ({nombre}) en regional {regional or "Sin especificar"}',
                                    datos_nuevos={
                                        'id_camaras': id_camaras,
                                        'nombre': nombre,
                                        'correo': correo,
                                        'estado': estado,
                                        'regional': regional,
                                        'latitud': latitud_val,
                                        'longitud': longitud_val
                                    }
                                )
                    
                elif accion == 'eliminar':
                    id_camaras = request.form.get('id_camaras')
                    
                    # Obtener datos de la cámara antes de eliminar para la bitácora
                    cur.execute("SELECT nombre, regional FROM camaras WHERE id_camaras = %s", (id_camaras,))
                    camara_data = cur.fetchone()
                    
                    cur.execute("DELETE FROM camaras WHERE id_camaras = %s", (id_camaras,))
                    mysql.connection.commit()
                    success = 'Cámara eliminada exitosamente'
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion='DELETE',
                        modulo='Cámaras',
                        descripcion=f'Eliminó la cámara {id_camaras}' + (f' ({camara_data["nombre"]})' if camara_data else ''),
                        datos_anteriores={
                            'id_camaras': id_camaras,
                            'nombre': camara_data['nombre'] if camara_data else None,
                            'regional': camara_data['regional'] if camara_data else None
                        }
                    )
                
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
                    latitud = request.form.get('latitud', '').strip()
                    longitud = request.form.get('longitud', '').strip()
                    
                    print(f"DEBUG: Editando cámara. ID original: '{id_camaras_original}', ID nuevo: '{id_camaras}'")  # Log para debug
                    
                    # Validar campos obligatorios
                    if not id_camaras:
                        error = 'El ID de la cámara es obligatorio'
                    elif not correo:
                        error = 'El correo electrónico es obligatorio'
                    elif not nombre:
                        error = 'El nombre es obligatorio'
                    else:
                        # Validar coordenadas si se proporcionan
                        latitud_val = None
                        longitud_val = None
                        if latitud and longitud:
                            try:
                                latitud_val = float(latitud)
                                longitud_val = float(longitud)
                                if not (-90 <= latitud_val <= 90):
                                    error = 'La latitud debe estar entre -90 y 90 grados'
                                elif not (-180 <= longitud_val <= 180):
                                    error = 'La longitud debe estar entre -180 y 180 grados'
                            except ValueError:
                                error = 'Las coordenadas deben ser números válidos'
                        elif latitud or longitud:
                            error = 'Debe proporcionar tanto latitud como longitud, o dejar ambos campos vacíos'
                        
                        # Si el ID cambió, verificar que el nuevo ID no exista en otra cámara
                        if not error and id_camaras != id_camaras_original:
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
                                    cambio_password = %s, usuario_id = %s, latitud = %s, longitud = %s
                                WHERE id_camaras = %s
                            """, (id_camaras, correo, nombre, estado, 
                                 regional if regional else None,
                                 fecha_creacion if fecha_creacion else None,
                                 fecha_ultima_modificacion if fecha_ultima_modificacion else None,
                                 cambio_password if cambio_password else None,
                                 usuario_id, latitud_val, longitud_val, id_camaras_original))
                            
                            mysql.connection.commit()
                            success = f'Cámara "{nombre}" actualizada exitosamente'
                            
                            # Registrar en bitácora
                            BitacoraController.registrar_accion(
                                accion='UPDATE',
                                modulo='Cámaras',
                                descripcion=f'Actualizó la cámara {id_camaras} ({nombre})',
                                datos_nuevos={
                                    'id_camaras': id_camaras,
                                    'id_camaras_original': id_camaras_original,
                                    'nombre': nombre,
                                    'correo': correo,
                                    'estado': estado,
                                    'regional': regional,
                                    'latitud': latitud_val,
                                    'longitud': longitud_val
                                }
                            )
                    
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
        
        # Registrar acceso al módulo de cámaras
        BitacoraController.registrar_accion(
            accion='VIEW',
            modulo='Cámaras',
            descripcion='Accedió al módulo de gestión de cámaras'
        )
        
        # Obtener cámaras con información de usuario y coordenadas
        cur.execute("""
            SELECT c.id_camaras, c.correo, c.nombre, c.estado, c.regional,
                   c.fecha_creacion, c.fecha_ultima_modificacion, c.cambio_password,
                   c.usuario_id, c.latitud, c.longitud,
                   u.nombre as usuario_nombre
            FROM camaras c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
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
        
        cur.close()
        
        return render_template('camaras.html',
                             camaras=camaras,
                             usuarios=usuarios,
                             usuario_actual=usuario_actual,
                             error=error,
                             success=success)
    
    @staticmethod
    def get_camara(id_camaras):
        """Get camera data by ID for editing"""
        try:
            cur = mysql.connection.cursor()
            
            cur.execute("""
                SELECT c.id_camaras, c.correo, c.nombre, c.estado, c.regional,
                       c.fecha_creacion, c.fecha_ultima_modificacion, c.cambio_password,
                       c.usuario_id, c.latitud, c.longitud,
                       u.nombre as usuario_nombre
                FROM camaras c
                LEFT JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.id_camaras = %s
            """, (id_camaras,))
            
            camara = cur.fetchone()
            cur.close()
            
            if camara:
                return jsonify({
                    'success': True,
                    'camara': {
                        'id_camaras': camara['id_camaras'],
                        'correo': camara['correo'],
                        'nombre': camara['nombre'],
                        'estado': camara['estado'],
                        'regional': camara['regional'],
                        'fecha_creacion': camara['fecha_creacion'].strftime('%Y-%m-%d') if camara['fecha_creacion'] else '',
                        'usuario_id': camara['usuario_id'],
                        'latitud': float(camara['latitud']) if camara['latitud'] else '',
                        'longitud': float(camara['longitud']) if camara['longitud'] else '',
                        'usuario_nombre': camara['usuario_nombre']
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Cámara no encontrada'})
                
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})