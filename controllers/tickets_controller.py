from flask import render_template, request, redirect, jsonify, session
import uuid
import datetime
from config import mysql
from controllers.bitacora_controller import BitacoraController

def generar_id_ticket():
    """Genera un ID único para tickets en formato: TC + YYYYMMDD + 10 """
   
    fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
    
    unique_part = str(uuid.uuid4()).replace('-', '')[:10].lower()
    return f"TC{fecha_actual}{unique_part}"

class TicketsController:
    @staticmethod
    def agregar_ticket():
        """Show form to add ticket"""
        try:
            cur = mysql.connection.cursor()
            
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
            
            # Obtener usuarios
            cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
            usuarios = cur.fetchall()
            
            # Obtener departamentos
            cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
            departamentos = cur.fetchall()
            
            # Obtener tipologías
            cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
            tipologias = cur.fetchall()
            
            # Obtener unidades (si existe la tabla)
            try:
                cur.execute("SELECT id, nombre FROM unidades ORDER BY nombre")
                unidades = cur.fetchall()
            except:
                unidades = []

            # Obtener despachos (si existe la tabla)
            try:
                cur.execute("SELECT id, nombre FROM despachos ORDER BY nombre")
                despachos = cur.fetchall()
            except:
                despachos = []
            
            cur.close()
            
            return render_template('agregar_ticket.html', 
                                 usuarios=usuarios,
                                 usuario_actual=usuario_actual,
                                 departamentos=departamentos, 
                                 tipologias=tipologias,
                                 unidades=unidades,
                                 despachos=despachos)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al cargar formulario: {str(e)}'
            })

    @staticmethod
    def editar_ticket(ticket_id):
        """Show form to edit ticket"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener datos del ticket
            cur.execute("""
                SELECT t.*, 
                       ST_X(t.location) as latitud, 
                       ST_Y(t.location) as longitud,
                       d.nombre as departamento_nombre,
                       m.nombre as municipio_nombre,
                       tip.nombre as tipologia_nombre,
                       stip.nombre as subtipologia_nombre,
                       u.nombre as usuario_nombre,
                       r.nombre as usuario_rol
                FROM tickets t
                LEFT JOIN departamentos d ON t.departamento_id = d.id
                LEFT JOIN municipios m ON t.municipio_id = m.id
                LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
                LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
                LEFT JOIN roles r ON ur.rol_id = r.id
                WHERE t.id = %s
            """, (ticket_id,))
            ticket = cur.fetchone()
            
            if not ticket:
                cur.close()
                return redirect('/tickets?error=Ticket no encontrado')
            
            # Obtener usuarios
            cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
            usuarios = cur.fetchall()
            
            # Obtener departamentos
            cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
            departamentos = cur.fetchall()
            
            # Obtener municipios del departamento actual
            municipios = []
            if ticket['departamento_id']:
                cur.execute("SELECT id, nombre FROM municipios WHERE departamento_id = %s ORDER BY nombre", 
                           (ticket['departamento_id'],))
                municipios = cur.fetchall()
            
            # Obtener tipologías
            cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
            tipologias = cur.fetchall()
            
            # Obtener subtipologías de la tipología actual
            subtipologias = []
            if ticket['tipologia_id']:
                cur.execute("SELECT id, nombre FROM subtipologias WHERE tipologia_id = %s ORDER BY nombre", 
                           (ticket['tipologia_id'],))
                subtipologias = cur.fetchall()
            
            cur.close()
            
            return render_template('editar_ticket.html', 
                                 ticket=ticket,
                                 usuarios=usuarios,
                                 departamentos=departamentos,
                                 municipios=municipios,
                                 tipologias=tipologias,
                                 subtipologias=subtipologias)
        except Exception as e:
            return redirect(f'/tickets?error=Error al cargar ticket: {str(e)}')

    @staticmethod
    def tickets():
        """Handle tickets management (create, edit, delete, list)"""
        if request.method == 'POST':
            try:
                cur = mysql.connection.cursor()
                
                # Verificar si es una acción de eliminar
                if request.form.get('action') == 'delete':
                    ticket_id = request.form.get('ticket_id')
                    
                    # Eliminar relaciones
                    cur.execute("DELETE FROM ticket_despacho WHERE ticket_id = %s", (ticket_id,))
                    cur.execute("DELETE FROM ticket_unidad WHERE ticket_id = %s", (ticket_id,))
                    
                    # Eliminar ticket
                    cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
                    mysql.connection.commit()
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion='DELETE',
                        modulo='Tickets',
                        descripcion=f'Eliminó el ticket {ticket_id}',
                        datos_anteriores={'ticket_id': ticket_id}
                    )
                    
                    cur.close()
                    
                    return jsonify({'success': True, 'message': 'Ticket eliminado'})
                
                # Obtener datos del formulario
                ticket_id = request.form.get('ticket_id', '0')
                fecha = request.form.get('fecha')
                regional = request.form.get('regional') or None
                id_usuario = request.form.get('id_usuario')
                id_departamento = request.form.get('id_departamento')
                id_municipio = request.form.get('id_municipio')
                id_tipologia = request.form.get('id_tipologia')
                id_subtipologia = request.form.get('id_subtipologia') or None
                latitud = request.form.get('latitud') or None
                longitud = request.form.get('longitud') or None
                descripcion = request.form.get('descripcion') or None
                nota_respaldo = request.form.get('nota_respaldo') or None
                id_mando = request.form.get('id_mando') or None
                registro = request.form.get('registro') or None
                nota_final = request.form.get('nota_final') or None
                
                if ticket_id == '0':
                    # Crear nuevo ticket
                    nuevo_ticket_id = generar_id_ticket()
                    
                    if latitud and longitud:
                        cur.execute("""
                        INSERT INTO tickets 
                        (id, fecha_hora, regional, usuario_id, departamento_id, municipio_id, tipologia_id, subtipologia_id, 
                         location, descripcion, nota_respaldo, mando, registro, nota_final)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, POINT(%s, %s), %s, %s, %s, %s, %s)
                        """, (nuevo_ticket_id, fecha, regional, id_usuario, id_departamento, id_municipio, id_tipologia, 
                              id_subtipologia, latitud, longitud, descripcion, nota_respaldo, 
                              id_mando, registro, nota_final))
                    else:
                        cur.execute("""
                        INSERT INTO tickets 
                        (id, fecha_hora, regional, usuario_id, departamento_id, municipio_id, tipologia_id, subtipologia_id, 
                         location, descripcion, nota_respaldo, mando, registro, nota_final)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, POINT(0, 0), %s, %s, %s, %s, %s)
                        """, (nuevo_ticket_id, fecha, regional, id_usuario, id_departamento, id_municipio, id_tipologia, 
                              id_subtipologia, descripcion, nota_respaldo, 
                              id_mando, registro, nota_final))
                    
                    ticket_id = nuevo_ticket_id
                    message = f'Ticket {ticket_id} creado exitosamente'
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion='CREATE',
                        modulo='Tickets',
                        descripcion=f'Creó el ticket {ticket_id} en {regional or "Sin regional"}',
                        datos_nuevos={
                            'ticket_id': ticket_id,
                            'fecha': fecha,
                            'regional': regional,
                            'departamento_id': id_departamento,
                            'municipio_id': id_municipio,
                            'tipologia_id': id_tipologia,
                            'descripcion': descripcion[:100] if descripcion else None
                        }
                    )
                else:
                    # Actualizar ticket existente
                    if latitud and longitud:
                        cur.execute("""
                        UPDATE tickets SET 
                            fecha_hora = %s, regional = %s, usuario_id = %s, departamento_id = %s, municipio_id = %s,
                            tipologia_id = %s, subtipologia_id = %s, location = POINT(%s, %s),
                            descripcion = %s, nota_respaldo = %s, mando = %s, registro = %s, nota_final = %s
                        WHERE id = %s
                        """, (fecha, regional, id_usuario, id_departamento, id_municipio, id_tipologia, 
                              id_subtipologia, latitud, longitud, descripcion, nota_respaldo, 
                              id_mando, registro, nota_final, ticket_id))
                    else:
                        cur.execute("""
                        UPDATE tickets SET 
                            fecha_hora = %s, regional = %s, usuario_id = %s, departamento_id = %s, municipio_id = %s,
                            tipologia_id = %s, subtipologia_id = %s,
                            descripcion = %s, nota_respaldo = %s, mando = %s, registro = %s, nota_final = %s
                        WHERE id = %s
                        """, (fecha, regional, id_usuario, id_departamento, id_municipio, id_tipologia, 
                              id_subtipologia, descripcion, nota_respaldo, 
                              id_mando, registro, nota_final, ticket_id))
                    
                    # Eliminar asignaciones anteriores
                    cur.execute("DELETE FROM ticket_despacho WHERE ticket_id = %s", (ticket_id,))
                    cur.execute("DELETE FROM ticket_unidad WHERE ticket_id = %s", (ticket_id,))
                    
                    message = f'Ticket #{ticket_id} actualizado exitosamente'
                    
                    # Registrar en bitácora
                    BitacoraController.registrar_accion(
                        accion='UPDATE',
                        modulo='Tickets',
                        descripcion=f'Actualizó el ticket {ticket_id}',
                        datos_nuevos={
                            'ticket_id': ticket_id,
                            'fecha': fecha,
                            'regional': regional,
                            'departamento_id': id_departamento,
                            'municipio_id': id_municipio,
                            'tipologia_id': id_tipologia,
                            'descripcion': descripcion[:100] if descripcion else None
                        }
                    )
                
                # Agregar asignaciones de despachos
                despachos_seleccionados = request.form.getlist('despachos')
                for despacho_id in despachos_seleccionados:
                    if despacho_id:
                        cur.execute("INSERT INTO ticket_despacho (ticket_id, despacho_id) VALUES (%s, %s)",
                                  (ticket_id, despacho_id))
                
                # Agregar asignaciones de unidades
                unidades_seleccionadas = request.form.getlist('unidades')
                for unidad_id in unidades_seleccionadas:
                    if unidad_id:
                        cur.execute("INSERT INTO ticket_unidad (ticket_id, unidad_id) VALUES (%s, %s)",
                                  (ticket_id, unidad_id))
                
                mysql.connection.commit()
                cur.close()
                
                # Redirigir con mensaje de éxito
                return redirect('/tickets' + f'?success={message}')
                
            except Exception as e:
                return redirect('/tickets' + f'?error=Error: {str(e)}')
        
        # GET - Mostrar página
        try:
            cur = mysql.connection.cursor()
            
            # Registrar acceso al módulo de tickets
            BitacoraController.registrar_accion(
                accion='VIEW',
                modulo='Tickets',
                descripcion='Accedió al módulo de gestión de tickets'
            )
            
            # Obtener todos los tickets
            cur.execute("""
            SELECT 
                t.id, t.fecha_hora, t.regional, t.descripcion, t.nota_respaldo, t.registro, t.nota_final,
                ST_X(t.location) as latitud, ST_Y(t.location) as longitud,
                d.nombre as departamento_nombre,
                m.nombre as municipio_nombre,
                tip.nombre as tipologia_nombre,
                stip.nombre as subtipologia_nombre,
                CONCAT(u.nombre) as usuario_nombre,
                r.nombre as usuario_rol,
                t.departamento_id as id_departamento, t.municipio_id as id_municipio, 
                t.tipologia_id as id_tipologia, t.subtipologia_id as id_subtipologia, 
                t.usuario_id as id_usuario
            FROM tickets t
            LEFT JOIN departamentos d ON t.departamento_id = d.id
            LEFT JOIN municipios m ON t.municipio_id = m.id
            LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
            LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
            LEFT JOIN usuarios u ON t.usuario_id = u.id
            LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
            ORDER BY t.fecha_hora DESC
            """)
            tickets = cur.fetchall()
            
            # Obtener datos para formulario
            cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
            usuarios = cur.fetchall()
            
            cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
            departamentos = cur.fetchall()
            
            cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
            tipologias = cur.fetchall()
            
            cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
            mandos = cur.fetchall()
            
            cur.execute("SELECT id, nombre FROM despachos ORDER BY nombre")
            despachos = cur.fetchall()
            
            cur.execute("SELECT id, nombre FROM unidades ORDER BY nombre")
            unidades = cur.fetchall()
            
            cur.close()
            
            # Obtener mensajes de la URL
            success = request.args.get('success')
            error = request.args.get('error')
            
            return render_template('tickets_lista.html',
                                 tickets=tickets,
                                 usuarios=usuarios,
                                 departamentos=departamentos,
                                 tipologias=tipologias,
                                 mandos=mandos,
                                 despachos=despachos,
                                 unidades=unidades,
                                 success=success,
                                 error=error)
        
        except Exception as e:
            return render_template('tickets.html', 
                                 error=f"Error al cargar tickets: {str(e)}", 
                                 tickets=[], 
                                 usuarios=[], 
                                 departamentos=[], 
                                 tipologias=[],
                                 mandos=[],
                                 despachos=[],
                                 unidades=[])

    @staticmethod
    def api_ticket_detalles(ticket_id):
        """API to get complete ticket details"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener datos básicos del ticket
            cur.execute("""
            SELECT 
                t.*, 
                ST_X(t.location) as latitud, ST_Y(t.location) as longitud,
                d.nombre as departamento,
                m.nombre as municipio,
                tip.nombre as tipologia,
                stip.nombre as subtipologia,
                u.nombre as usuario,
                r.nombre as usuario_rol,
                t.mando as mando_nombre
            FROM tickets t
            LEFT JOIN departamentos d ON t.departamento_id = d.id
            LEFT JOIN municipios m ON t.municipio_id = m.id
            LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
            LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
            LEFT JOIN usuarios u ON t.usuario_id = u.id
            LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
            LEFT JOIN roles r ON ur.rol_id = r.id
            WHERE t.id = %s
            """, (ticket_id,))
            
            ticket = cur.fetchone()
            
            if not ticket:
                cur.close()
                return jsonify({'success': False, 'message': 'Ticket no encontrado'})
            
            # Formatear fecha para datetime-local input
            fecha_formatted = ''
            if ticket['fecha']:
                fecha_formatted = ticket['fecha'].strftime('%Y-%m-%dT%H:%M')
            
            # Formatear coordenadas para mostrar
            if ticket['latitud'] and ticket['longitud']:
                coordenadas = f"{ticket['latitud']:.6f}, {ticket['longitud']:.6f}"
            else:
                coordenadas = 'No disponible'
            
            # Obtener despachos asignados
            cur.execute("SELECT despacho_id FROM ticket_despacho WHERE ticket_id = %s", (ticket_id,))
            despachos_asignados = [row['despacho_id'] for row in cur.fetchall()]
            
            # Obtener unidades asignadas
            cur.execute("SELECT unidad_id FROM ticket_unidad WHERE ticket_id = %s", (ticket_id,))
            unidades_asignadas = [row['unidad_id'] for row in cur.fetchall()]
            
            cur.close()
            
            return jsonify({
                'success': True, 
                'ticket': {
                    'id': ticket['id'],
                    'fecha': ticket['fecha'].strftime('%d/%m/%Y %H:%M') if ticket['fecha'] else '',
                    'departamento': ticket['departamento'],
                    'municipio': ticket['municipio'],
                    'tipologia': ticket['tipologia'],
                    'subtipologia': ticket['subtipologia'],
                    'usuario': ticket['usuario'],
                    'mando': ticket['mando'],
                    'coordenadas': coordenadas,
                    'descripcion': ticket['descripcion'],
                    'nota_respaldo': ticket['nota_respaldo'],
                    'registro': ticket['registro'],
                    'nota_final': ticket['nota_final']
                },
                'ticket_data': {
                    'id': ticket['id'],
                    'fecha': fecha_formatted,
                    'regional': ticket['regional'],
                    'id_usuario': ticket['usuario_id'],
                    'id_departamento': ticket['departamento_id'],
                    'id_municipio': ticket['municipio_id'],
                    'id_tipologia': ticket['tipologia_id'],
                    'id_subtipologia': ticket['subtipologia_id'],
                    'id_mando': ticket['mando'],  # Como es TEXT, no hay id_mando
                    'latitud': ticket['latitud'],
                    'longitud': ticket['longitud'],
                    'descripcion': ticket['descripcion'],
                    'nota_respaldo': ticket['nota_respaldo'],
                    'registro': ticket['registro'],
                    'nota_final': ticket['nota_final'],
                    'despachos': despachos_asignados,
                    'unidades': unidades_asignadas
                }
            })
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    @staticmethod
    def detalle_ticket(ticket_id):
        """Show detailed view of a specific ticket"""
        try:
            cur = mysql.connection.cursor()
            
            # Registrar acceso al detalle del ticket
            BitacoraController.registrar_accion(
                accion='VIEW',
                modulo='Tickets',
                descripcion=f'Consultó detalles del ticket {ticket_id}'
            )
            
            # Obtener datos completos del ticket
            cur.execute("""
                SELECT t.*, 
                       ST_X(t.location) as latitud, 
                       ST_Y(t.location) as longitud,
                       d.nombre as departamento_nombre,
                       m.nombre as municipio_nombre,
                       tip.nombre as tipologia_nombre,
                       stip.nombre as subtipologia_nombre,
                       u.nombre as usuario_nombre,
                       u.usuario as usuario_login,
                       r.nombre as usuario_rol
                FROM tickets t
                LEFT JOIN departamentos d ON t.departamento_id = d.id
                LEFT JOIN municipios m ON t.municipio_id = m.id
                LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
                LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
                LEFT JOIN roles r ON ur.rol_id = r.id
                WHERE t.id = %s
            """, (ticket_id,))
            ticket = cur.fetchone()
            
            if not ticket:
                cur.close()
                return redirect('/tickets?error=Ticket no encontrado')
            
            # Obtener despachos asignados
            cur.execute("""
                SELECT d.nombre 
                FROM despachos d 
                JOIN ticket_despacho td ON d.id = td.despacho_id 
                WHERE td.ticket_id = %s
            """, (ticket_id,))
            despachos = [row['nombre'] for row in cur.fetchall()]
            
            # Obtener unidades asignadas
            cur.execute("""
                SELECT u.nombre 
                FROM unidades u 
                JOIN ticket_unidad tu ON u.id = tu.unidad_id 
                WHERE tu.ticket_id = %s
            """, (ticket_id,))
            unidades = [row['nombre'] for row in cur.fetchall()]
            
            cur.close()
            
            return render_template('detalle_ticket.html', 
                                 ticket=ticket,
                                 despachos=despachos,
                                 unidades=unidades)
                                 
        except Exception as e:
            return redirect(f'/tickets?error=Error al cargar ticket: {str(e)}')