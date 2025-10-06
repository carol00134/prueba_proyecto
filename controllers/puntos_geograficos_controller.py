from flask import render_template, request, session
from config import mysql
from controllers.bitacora_controller import BitacoraController

class PuntosGeograficosController:
    @staticmethod
    def puntos_geograficos():
        """Handle geographic points management"""
        error = None
        success = None
        
        if request.method == 'POST':
            accion = request.form.get('accion')
            
            cur = mysql.connection.cursor()
            
            try:
                if accion == 'agregar':
                    nombre = request.form.get('nombre')
                    descripcion = request.form.get('descripcion')
                    departamento_id = request.form.get('departamento_id')
                    municipio_id = request.form.get('municipio_id')
                    direccion = request.form.get('direccion')
                    latitud = request.form.get('latitud')
                    longitud = request.form.get('longitud')
                    
                    if not all([nombre, departamento_id, municipio_id, latitud, longitud]):
                        error = 'Por favor complete todos los campos obligatorios'
                    else:
                        # Crear el punto geográfico con POINT
                        point_wkt = f"POINT({longitud} {latitud})"
                        
                        cur.execute("""
                            INSERT INTO puntos_geograficos 
                            (nombre, descripcion, departamento_id, municipio_id, direccion, location, usuario_id) 
                            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s), %s)
                        """, (nombre, descripcion, departamento_id, municipio_id, direccion, point_wkt, session.get('user_id')))
                        
                        mysql.connection.commit()
                        success = f'Punto geográfico "{nombre}" agregado exitosamente'
                        
                        # Registrar en bitácora
                        BitacoraController.registrar_accion(
                            accion='CREATE',
                            modulo='Puntos Geográficos',
                            descripcion=f'Creó el punto geográfico "{nombre}" en {direccion or "ubicación no especificada"}',
                            datos_nuevos={
                                'nombre': nombre,
                                'descripcion': descripcion,
                                'departamento_id': departamento_id,
                                'municipio_id': municipio_id,
                                'direccion': direccion,
                                'latitud': latitud,
                                'longitud': longitud
                            }
                        )
                        
                elif accion == 'eliminar':
                    punto_id = request.form.get('id')
                    
                    # Obtener datos del punto antes de eliminar
                    cur.execute("SELECT nombre, direccion FROM puntos_geograficos WHERE id = %s", (punto_id,))
                    punto_data = cur.fetchone()
                    
                    cur.execute("DELETE FROM puntos_geograficos WHERE id = %s", (punto_id,))
                    mysql.connection.commit()
                    success = 'Punto geográfico eliminado exitosamente'
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion='DELETE',
                        modulo='Puntos Geográficos',
                        descripcion=f'Eliminó el punto geográfico' + (f' "{punto_data["nombre"]}"' if punto_data else f' ID {punto_id}'),
                        datos_anteriores={
                            'id': punto_id,
                            'nombre': punto_data['nombre'] if punto_data else None,
                            'direccion': punto_data['direccion'] if punto_data else None
                        }
                    )
                
                elif accion == 'editar':
                    punto_id = request.form.get('id')
                    nombre = request.form.get('nombre')
                    descripcion = request.form.get('descripcion')
                    departamento_id = request.form.get('departamento_id')
                    municipio_id = request.form.get('municipio_id')
                    direccion = request.form.get('direccion')
                    latitud = request.form.get('latitud')
                    longitud = request.form.get('longitud')
                    
                    if not all([punto_id, nombre, departamento_id, municipio_id, latitud, longitud]):
                        error = 'Por favor complete todos los campos obligatorios'
                    else:
                        # Actualizar el punto geográfico con POINT
                        point_wkt = f"POINT({longitud} {latitud})"
                        
                        cur.execute("""
                            UPDATE puntos_geograficos 
                            SET nombre = %s, descripcion = %s, departamento_id = %s, 
                                municipio_id = %s, direccion = %s, location = ST_GeomFromText(%s)
                            WHERE id = %s
                        """, (nombre, descripcion, departamento_id, municipio_id, direccion, point_wkt, punto_id))
                        
                        mysql.connection.commit()
                        success = f'Punto geográfico "{nombre}" actualizado exitosamente'
                        
                        # Registrar en bitácora
                        BitacoraController.registrar_accion(
                            accion='UPDATE',
                            modulo='Puntos Geográficos',
                            descripcion=f'Actualizó el punto geográfico "{nombre}"',
                            datos_nuevos={
                                'id': punto_id,
                                'nombre': nombre,
                                'descripcion': descripcion,
                                'departamento_id': departamento_id,
                                'municipio_id': municipio_id,
                                'direccion': direccion,
                                'latitud': latitud,
                                'longitud': longitud
                            }
                        )
                    
            except Exception as e:
                error = f'Error: {str(e)}'
            finally:
                cur.close()
        
        # Obtener datos para mostrar
        cur = mysql.connection.cursor()
        
        # Registrar acceso al módulo de puntos geográficos
        BitacoraController.registrar_accion(
            accion='VIEW',
            modulo='Puntos Geográficos',
            descripcion='Accedió al módulo de puntos geográficos'
        )
        
        # Obtener departamentos
        cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
        departamentos = cur.fetchall()
        
        # Obtener puntos geográficos con información relacionada
        cur.execute("""
            SELECT pg.id, pg.nombre, pg.descripcion, pg.direccion, pg.fecha_registro,
                   ST_X(pg.location) as longitud, ST_Y(pg.location) as latitud,
                   d.nombre as departamento_nombre, m.nombre as municipio_nombre,
                   u.nombre as usuario_nombre
            FROM puntos_geograficos pg
            LEFT JOIN departamentos d ON pg.departamento_id = d.id
            LEFT JOIN municipios m ON pg.municipio_id = m.id
            LEFT JOIN usuarios u ON pg.usuario_id = u.id
            WHERE pg.activo = TRUE
            ORDER BY pg.fecha_registro DESC
        """)
        puntos_geograficos = cur.fetchall()
        
        cur.close()
        
        return render_template('puntoGeografico.html', 
                             departamentos=departamentos,
                             puntos_geograficos=puntos_geograficos,
                             error=error,
                             success=success)