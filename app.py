from flask import Flask
from flask import render_template, redirect, request, Response, session, jsonify, url_for
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder='template')


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = ''  
from flask import Flask
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder='template')


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = ''  
app.config['MYSQL_DB'] = 'proyecto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    if 'usuario' in session:
        cur = mysql.connection.cursor()
        
        # Contar usuarios activos
        cur.execute("SELECT COUNT(*) AS activos FROM usuarios WHERE activo = 1")
        usuarios_activos = cur.fetchone()['activos']
        
        # Contar tickets totales (como no hay estado, contamos todos)
        cur.execute("SELECT COUNT(*) AS total_tickets FROM tickets")
        tickets_nuevos = cur.fetchone()['total_tickets']
        
        # Contar puntos geográficos registrados
        cur.execute("SELECT COUNT(*) AS total_puntos FROM puntos_geograficos")
        puntos_geograficos = cur.fetchone()['total_puntos']
        
        # Obtener hora actual del servidor
        cur.execute("SELECT NOW() as hora_actual")
        hora_actual = cur.fetchone()['hora_actual']
        
        # Verificar conectividad de la base de datos (si llegamos aquí, está conectada)
        estado_bd = "En línea"
        
        cur.close()
        
        return render_template('index.html', 
                             usuarios_activos=usuarios_activos,
                             tickets_nuevos=tickets_nuevos,
                             puntos_geograficos=puntos_geograficos,
                             hora_actual=hora_actual,
                             estado_bd=estado_bd)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
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
                return redirect('/')
            else:
                return render_template('login.html', error='Contraseña incorrecta')
        else:
            return render_template('login.html', error='Usuario no encontrado')
    return render_template('login.html')
 
    
@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
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
        
        if accion == 'agregar':
            try:
                if not all([username, password, nombre, rol]):
                    error = 'Por favor complete todos los campos obligatorios'
                else:
                    hashed_password = generate_password_hash(password)
                    cur.execute("INSERT INTO usuarios (nombre, usuario, contraseña, rol) VALUES (%s, %s, %s, %s)", 
                               (nombre, username, hashed_password, rol))
                    mysql.connection.commit()
                    success = f'Usuario {username} creado exitosamente'
            except Exception as e:
                error = f'Error al crear usuario: {str(e)}'
                
        elif accion == 'editar':
            try:
                if not all([username, nombre, rol]):
                    error = 'Por favor complete todos los campos obligatorios'
                else:
                    # Actualizar información del usuario
                    if password:
                        hashed_password = generate_password_hash(password)
                        cur.execute("UPDATE usuarios SET nombre = %s, contraseña = %s, rol = %s WHERE usuario = %s", 
                                   (nombre, hashed_password, rol, username))
                    else:
                        cur.execute("UPDATE usuarios SET nombre = %s, rol = %s WHERE usuario = %s", 
                                   (nombre, rol, username))
                    
                    mysql.connection.commit()
                    success = f'Usuario {username} actualizado exitosamente'
                    usuario_editar = None
            except Exception as e:
                error = f'Error al actualizar usuario: {str(e)}'
                
        elif accion == 'eliminar':
            try:
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
                SELECT u.nombre, u.usuario, u.rol
                FROM usuarios u
                WHERE u.usuario = %s
            """, (username,))
            usuario_editar = cur.fetchone()
            
        elif accion == 'cancelar':
            usuario_editar = None
    
    # Obtener lista de usuarios
    cur.execute("""
        SELECT u.nombre, u.usuario, u.rol
        FROM usuarios u
        ORDER BY u.nombre, u.usuario
    """)
    usuarios = cur.fetchall()
    cur.close()
    
    return render_template('usuarios.html', 
                         usuarios=usuarios, 
                         usuario_editar=usuario_editar,
                         error=error,
                         success=success)


@app.route('/mapas')
def mapas():
    return render_template('mapas.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
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

def get_form_data():
    """Obtiene los datos necesarios para el formulario"""
    cur = mysql.connection.cursor()
    
    # Obtener departamentos
    cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
    departamentos = cur.fetchall()
    
    # Obtener tipologías
    cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
    tipologias = cur.fetchall()
    
    # Obtener despachos
    cur.execute("SELECT id, nombre FROM despachos ORDER BY nombre")
    despachos = cur.fetchall()
    
    # Obtener unidades
    cur.execute("SELECT id, nombre FROM unidades ORDER BY nombre")
    unidades = cur.fetchall()
    
    cur.close()
    
    return {
        'departamentos': departamentos,
        'tipologias': tipologias,
        'despachos': despachos,
        'unidades': unidades
    }

@app.route('/puntoGeografico', methods=['GET', 'POST'])
@app.route('/puntos_geograficos', methods=['GET', 'POST'])
def puntos_geograficos():
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
                    
            elif accion == 'eliminar':
                punto_id = request.form.get('id')
                cur.execute("DELETE FROM puntos_geograficos WHERE id = %s", (punto_id,))
                mysql.connection.commit()
                success = 'Punto geográfico eliminado exitosamente'
                
        except Exception as e:
            error = f'Error: {str(e)}'
        finally:
            cur.close()
    
    # Obtener datos para mostrar
    cur = mysql.connection.cursor()
    
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



from flask import jsonify

@app.route('/api/puntos')
def api_puntos():
    municipio = request.args.get('municipio', '')
    tipologia = request.args.get('tipologia', '')
    fecha = request.args.get('fecha', '')
    cur = mysql.connection.cursor()
    query = '''
        SELECT t.id, m.nombre AS municipio, tp.nombre AS tipologia, t.fecha,
               ST_X(t.location) AS lat, ST_Y(t.location) AS lng
        FROM tickets t
        JOIN municipios m ON t.municipio_id = m.id
        JOIN tipologias tp ON t.tipologia_id = tp.id
        WHERE 1=1
    '''
    params = []
    if municipio:
        query += " AND m.nombre LIKE %s"
        params.append(f"%{municipio}%")
    if tipologia:
        query += " AND tp.nombre LIKE %s"
        params.append(f"%{tipologia}%")
    if fecha:
        query += " AND DATE(t.fecha) = %s"
        params.append(fecha)
    cur.execute(query, params)
    resultados = cur.fetchall()
    cur.close()
    puntos = []
    for r in resultados:
        puntos.append({
            'id': r['id'],
            'municipio': r['municipio'],
            'tipologia': r['tipologia'],
            'fecha': r['fecha'],
            'lat': r['lat'],
            'lng': r['lng']
        })
    return jsonify(puntos)

@app.route('/api/usuarios_activos')
def api_usuarios_activos():
    cur = mysql.connection.cursor()
    # Contar todos los usuarios registrados
    cur.execute('SELECT COUNT(*) AS activos FROM usuarios')
    activos = cur.fetchone()['activos']
    cur.close()
    return jsonify({'activos': activos})

@app.route('/api/municipios/<int:departamento_id>')
def api_municipios(departamento_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre FROM municipios WHERE departamento_id = %s ORDER BY nombre", 
                (departamento_id,))
    municipios = cur.fetchall()
    cur.close()
    return jsonify(municipios)

@app.route('/api/subtipologias/<int:tipologia_id>')
def api_subtipologias(tipologia_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, nombre FROM subtipologias WHERE tipologia_id = %s ORDER BY nombre", 
                (tipologia_id,))
    subtipologias = cur.fetchall()
    cur.close()
    return jsonify(subtipologias)

@app.route('/catalogos', methods=['GET', 'POST'])
def catalogos():
    error = None
    success = None
    
    if request.method == 'POST':
        tabla = request.form.get('tabla')
        accion = request.form.get('accion')
        nombre = request.form.get('nombre')
        
        cur = mysql.connection.cursor()
        
        try:
            if accion == 'agregar':
                if tabla == 'departamentos':
                    cur.execute("INSERT INTO departamentos (nombre) VALUES (%s)", (nombre,))
                    success = f'Departamento "{nombre}" agregado exitosamente'
                    
                elif tabla == 'municipios':
                    departamento_id = request.form.get('departamento_id')
                    cur.execute("INSERT INTO municipios (nombre, departamento_id) VALUES (%s, %s)", 
                               (nombre, departamento_id))
                    success = f'Municipio "{nombre}" agregado exitosamente'
                    
                elif tabla == 'tipologias':
                    cur.execute("INSERT INTO tipologias (nombre) VALUES (%s)", (nombre,))
                    success = f'Tipología "{nombre}" agregada exitosamente'
                    
                elif tabla == 'despachos':
                    cur.execute("INSERT INTO despachos (nombre) VALUES (%s)", (nombre,))
                    success = f'Despacho "{nombre}" agregado exitosamente'
                    
                elif tabla == 'unidades':
                    cur.execute("INSERT INTO unidades (nombre) VALUES (%s)", (nombre,))
                    success = f'Unidad "{nombre}" agregada exitosamente'
                    
                mysql.connection.commit()
                
            elif accion == 'editar':
                item_id = request.form.get('id')
                if tabla == 'departamentos':
                    cur.execute("UPDATE departamentos SET nombre = %s WHERE id = %s", (nombre, item_id))
                    success = f'Departamento actualizado exitosamente'
                elif tabla == 'municipios':
                    cur.execute("UPDATE municipios SET nombre = %s WHERE id = %s", (nombre, item_id))
                    success = f'Municipio actualizado exitosamente'
                elif tabla == 'tipologias':
                    cur.execute("UPDATE tipologias SET nombre = %s WHERE id = %s", (nombre, item_id))
                    success = f'Tipología actualizada exitosamente'
                elif tabla == 'despachos':
                    cur.execute("UPDATE despachos SET nombre = %s WHERE id = %s", (nombre, item_id))
                    success = f'Despacho actualizado exitosamente'
                elif tabla == 'unidades':
                    cur.execute("UPDATE unidades SET nombre = %s WHERE id = %s", (nombre, item_id))
                    success = f'Unidad actualizada exitosamente'
                    
                mysql.connection.commit()
                
            elif accion == 'eliminar':
                item_id = request.form.get('id')
                if tabla == 'departamentos':
                    cur.execute("DELETE FROM departamentos WHERE id = %s", (item_id,))
                elif tabla == 'municipios':
                    cur.execute("DELETE FROM municipios WHERE id = %s", (item_id,))
                elif tabla == 'tipologias':
                    cur.execute("DELETE FROM tipologias WHERE id = %s", (item_id,))
                elif tabla == 'despachos':
                    cur.execute("DELETE FROM despachos WHERE id = %s", (item_id,))
                elif tabla == 'unidades':
                    cur.execute("DELETE FROM unidades WHERE id = %s", (item_id,))
                    
                mysql.connection.commit()
                success = f'Elemento eliminado exitosamente'
                
        except Exception as e:
            error = f'Error: {str(e)}'
        finally:
            cur.close()
    
    # Obtener datos para mostrar
    cur = mysql.connection.cursor()
    
    # Departamentos con conteo de municipios
    cur.execute("""
        SELECT d.id, d.nombre, COUNT(m.id) as municipios_count
        FROM departamentos d
        LEFT JOIN municipios m ON d.id = m.departamento_id
        GROUP BY d.id, d.nombre
        ORDER BY d.nombre
    """)
    departamentos = cur.fetchall()
    
    # Municipios con nombre de departamento
    cur.execute("""
        SELECT m.id, m.nombre, d.nombre as departamento_nombre
        FROM municipios m
        JOIN departamentos d ON m.departamento_id = d.id
        ORDER BY d.nombre, m.nombre
    """)
    municipios = cur.fetchall()
    
    # Tipologías con conteo de subtipologías
    cur.execute("""
        SELECT t.id, t.nombre, COUNT(st.id) as subtipologias_count
        FROM tipologias t
        LEFT JOIN subtipologias st ON t.id = st.tipologia_id
        GROUP BY t.id, t.nombre
        ORDER BY t.nombre
    """)
    tipologias = cur.fetchall()
    
    # Despachos
    cur.execute("SELECT id, nombre FROM despachos ORDER BY nombre")
    despachos = cur.fetchall()
    
    # Unidades
    cur.execute("SELECT id, nombre FROM unidades ORDER BY nombre")
    unidades = cur.fetchall()
    
    cur.close()
    
    return render_template('catalogos.html',
                         departamentos=departamentos,
                         municipios=municipios,
                         tipologias=tipologias,
                         despachos=despachos,
                         unidades=unidades,
                         error=error,
                         success=success)

@app.route('/poblar_datos')
def poblar_datos():
    """Ruta temporal para poblar datos iniciales - ELIMINAR EN PRODUCCIÓN"""
    cur = mysql.connection.cursor()
    
    try:
        # Crear roles básicos
        roles = ['admin', 'operador', 'supervisor', 'invitado']
        for rol in roles:
            cur.execute("INSERT IGNORE INTO roles (nombre) VALUES (%s)", (rol,))
        
        # Departamentos de ejemplo
        departamentos = [
            'Antioquia', 'Atlántico', 'Bogotá D.C.', 'Bolívar', 'Boyacá',
            'Caldas', 'Caquetá', 'Cauca', 'César', 'Córdoba',
            'Cundinamarca', 'Chocó', 'Huila', 'La Guajira', 'Magdalena',
            'Meta', 'Nariño', 'Norte de Santander', 'Quindío', 'Risaralda',
            'Santander', 'Sucre', 'Tolima', 'Valle del Cauca'
        ]
        
        for depto in departamentos:
            cur.execute("INSERT IGNORE INTO departamentos (nombre) VALUES (%s)", (depto,))
        
        # Obtener ID de Antioquia para municipios de ejemplo
        cur.execute("SELECT id FROM departamentos WHERE nombre = 'Antioquia'")
        antioquia_result = cur.fetchone()
        if antioquia_result:
            antioquia_id = antioquia_result['id']
            
            # Municipios de ejemplo para Antioquia
            municipios_antioquia = [
                'Medellín', 'Bello', 'Itagüí', 'Envigado', 'Rionegro',
                'Sabaneta', 'Copacabana', 'La Estrella', 'Caldas', 'Barbosa'
            ]
            
            for municipio in municipios_antioquia:
                cur.execute("INSERT IGNORE INTO municipios (nombre, departamento_id) VALUES (%s, %s)", 
                           (municipio, antioquia_id))
        
        # Tipologías de ejemplo
        tipologias = [
            'Emergencia Médica', 'Incendio', 'Accidente de Tránsito', 
            'Desastre Natural', 'Seguridad Ciudadana', 'Rescate',
            'Emergencia Ambiental', 'Apoyo Logístico'
        ]
        
        for tipo in tipologias:
            cur.execute("INSERT IGNORE INTO tipologias (nombre) VALUES (%s)", (tipo,))
        
        # Obtener ID de tipología para subtipologías
        cur.execute("SELECT id FROM tipologias WHERE nombre = 'Emergencia Médica'")
        emergencia_result = cur.fetchone()
        if emergencia_result:
            emergencia_id = emergencia_result['id']
            
            # Subtipologías de ejemplo
            subtipologias_emergencia = [
                'Infarto', 'Accidente Cerebrovascular', 'Trauma', 
                'Intoxicación', 'Parto de Emergencia'
            ]
            
            for subtipo in subtipologias_emergencia:
                cur.execute("INSERT IGNORE INTO subtipologias (nombre, tipologia_id) VALUES (%s, %s)", 
                           (subtipo, emergencia_id))
        
        # Despachos de ejemplo
        despachos = [
            'Cruz Roja', 'Bomberos', 'Policía Nacional', 'Defensa Civil',
            'Ejército Nacional', 'Hospital General', 'Ambulancia Básica',
            'Ambulancia Medicalizada'
        ]
        
        for despacho in despachos:
            cur.execute("INSERT IGNORE INTO despachos (nombre) VALUES (%s)", (despacho,))
        
        # Unidades de ejemplo
        unidades = [
            'Ambulancia AMB-001', 'Ambulancia AMB-002', 'Carro Bomba CB-001',
            'Patrulla POL-001', 'Patrulla POL-002', 'Helicóptero HEL-001',
            'Unidad de Rescate RES-001', 'Motocicleta MOT-001'
        ]
        
        for unidad in unidades:
            cur.execute("INSERT IGNORE INTO unidades (nombre) VALUES (%s)", (unidad,))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Datos iniciales poblados exitosamente'
        })
        
    except Exception as e:
        cur.close()
        return jsonify({
            'status': 'error',
            'message': f'Error al poblar datos: {str(e)}'
        })

# Mostrar formulario para agregar ticket
@app.route('/agregar_ticket')
def agregar_ticket():
    try:
        cur = mysql.connection.cursor()
        
        # Obtener usuarios
        cur.execute("SELECT id, nombre, usuario FROM usuarios ORDER BY nombre")
        usuarios = cur.fetchall()
        
        # Obtener departamentos
        cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
        departamentos = cur.fetchall()
        
        # Obtener tipologías
        cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
        tipologias = cur.fetchall()
        
        # Obtener agentes (si existe la tabla)
        try:
            cur.execute("SELECT id, nombre FROM agentes ORDER BY nombre")
            agentes = cur.fetchall()
        except:
            agentes = []
        
        # Obtener unidades (si existe la tabla)
        try:
            cur.execute("SELECT id, nombre FROM unidades ORDER BY nombre")
            unidades = cur.fetchall()
        except:
            unidades = []
        
        cur.close()
        
        return render_template('agregar_ticket.html', 
                             usuarios=usuarios,
                             departamentos=departamentos, 
                             tipologias=tipologias,
                             agentes=agentes,
                             unidades=unidades)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar formulario: {str(e)}'
        })

# Mostrar formulario para editar ticket
@app.route('/editar_ticket/<int:ticket_id>')
def editar_ticket(ticket_id):
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
                   u.rol as usuario_rol
            FROM tickets t
            LEFT JOIN departamentos d ON t.departamento_id = d.id
            LEFT JOIN municipios m ON t.municipio_id = m.id
            LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
            LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
            LEFT JOIN usuarios u ON t.usuario_id = u.id
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

# Gestión completa de tickets (crear, editar, eliminar, listar)
@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
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
                cur.close()
                
                return jsonify({'success': True, 'message': 'Ticket eliminado'})
            
            # Obtener datos del formulario
            ticket_id = request.form.get('ticket_id', '0')
            fecha = request.form.get('fecha')
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
                if latitud and longitud:
                    cur.execute("""
                    INSERT INTO tickets 
                    (fecha, usuario_id, departamento_id, municipio_id, tipologia_id, subtipologia_id, 
                     location, descripcion, nota_respaldo, mando, registro, nota_final)
                    VALUES (%s, %s, %s, %s, %s, %s, POINT(%s, %s), %s, %s, %s, %s, %s)
                    """, (fecha, id_usuario, id_departamento, id_municipio, id_tipologia, 
                          id_subtipologia, latitud, longitud, descripcion, nota_respaldo, 
                          id_mando, registro, nota_final))
                else:
                    cur.execute("""
                    INSERT INTO tickets 
                    (fecha, usuario_id, departamento_id, municipio_id, tipologia_id, subtipologia_id, 
                     location, descripcion, nota_respaldo, mando, registro, nota_final)
                    VALUES (%s, %s, %s, %s, %s, %s, POINT(0, 0), %s, %s, %s, %s, %s)
                    """, (fecha, id_usuario, id_departamento, id_municipio, id_tipologia, 
                          id_subtipologia, descripcion, nota_respaldo, 
                          id_mando, registro, nota_final))
                
                ticket_id = cur.lastrowid
                message = f'Ticket #{ticket_id} creado exitosamente'
            else:
                # Actualizar ticket existente
                if latitud and longitud:
                    cur.execute("""
                    UPDATE tickets SET 
                        fecha = %s, usuario_id = %s, departamento_id = %s, municipio_id = %s,
                        tipologia_id = %s, subtipologia_id = %s, location = POINT(%s, %s),
                        descripcion = %s, nota_respaldo = %s, mando = %s, registro = %s, nota_final = %s
                    WHERE id = %s
                    """, (fecha, id_usuario, id_departamento, id_municipio, id_tipologia, 
                          id_subtipologia, latitud, longitud, descripcion, nota_respaldo, 
                          id_mando, registro, nota_final, ticket_id))
                else:
                    cur.execute("""
                    UPDATE tickets SET 
                        fecha = %s, usuario_id = %s, departamento_id = %s, municipio_id = %s,
                        tipologia_id = %s, subtipologia_id = %s,
                        descripcion = %s, nota_respaldo = %s, mando = %s, registro = %s, nota_final = %s
                    WHERE id = %s
                    """, (fecha, id_usuario, id_departamento, id_municipio, id_tipologia, 
                          id_subtipologia, descripcion, nota_respaldo, 
                          id_mando, registro, nota_final, ticket_id))
                
                # Eliminar asignaciones anteriores
                cur.execute("DELETE FROM ticket_despacho WHERE ticket_id = %s", (ticket_id,))
                cur.execute("DELETE FROM ticket_unidad WHERE ticket_id = %s", (ticket_id,))
                
                message = f'Ticket #{ticket_id} actualizado exitosamente'
            
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
            return redirect(url_for('tickets') + f'?success={message}')
            
        except Exception as e:
            return redirect(url_for('tickets') + f'?error=Error: {str(e)}')
    
    # GET - Mostrar página
    try:
        cur = mysql.connection.cursor()
        
        # Obtener todos los tickets
        cur.execute("""
        SELECT 
            t.id, t.fecha, t.descripcion, t.nota_respaldo, t.registro, t.nota_final,
            ST_X(t.location) as latitud, ST_Y(t.location) as longitud,
            d.nombre as departamento_nombre,
            m.nombre as municipio_nombre,
            tip.nombre as tipologia_nombre,
            stip.nombre as subtipologia_nombre,
            CONCAT(u.nombre) as usuario_nombre,
            u.rol as usuario_rol,
            t.departamento_id as id_departamento, t.municipio_id as id_municipio, 
            t.tipologia_id as id_tipologia, t.subtipologia_id as id_subtipologia, 
            t.usuario_id as id_usuario
        FROM tickets t
        LEFT JOIN departamentos d ON t.departamento_id = d.id
        LEFT JOIN municipios m ON t.municipio_id = m.id
        LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
        LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
        LEFT JOIN usuarios u ON t.usuario_id = u.id
        ORDER BY t.fecha DESC
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
    try:
        cur = mysql.connection.cursor()
        
        # Construir la consulta base
        query = """
        SELECT 
            t.id, t.fecha, t.descripcion, t.nota_respaldo, t.registro, t.nota_final,
            ST_X(t.location) as latitud, ST_Y(t.location) as longitud,
            d.nombre as departamento_nombre,
            m.nombre as municipio_nombre,
            tip.nombre as tipologia_nombre,
            stip.nombre as subtipologia_nombre,
            u.nombre as usuario_nombre,
            u.rol as usuario_rol,
            t.departamento_id as id_departamento, t.municipio_id as id_municipio, 
            t.tipologia_id as id_tipologia, t.subtipologia_id as id_subtipologia, 
            t.usuario_id as id_usuario
        FROM tickets t
        LEFT JOIN departamentos d ON t.departamento_id = d.id
        LEFT JOIN municipios m ON t.municipio_id = m.id
        LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
        LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
        LEFT JOIN usuarios u ON t.usuario_id = u.id
        WHERE 1=1
        """
        
        # Agregar filtros
        params = []
        
        if request.args.get('departamento'):
            query += " AND t.departamento_id = %s"
            params.append(request.args.get('departamento'))
        
        if request.args.get('tipologia'):
            query += " AND t.tipologia_id = %s"
            params.append(request.args.get('tipologia'))
        
        if request.args.get('fecha_desde'):
            query += " AND DATE(t.fecha) >= %s"
            params.append(request.args.get('fecha_desde'))
        
        if request.args.get('fecha_hasta'):
            query += " AND DATE(t.fecha) <= %s"
            params.append(request.args.get('fecha_hasta'))
        
        query += " ORDER BY t.fecha DESC"
        
        cur.execute(query, params)
        tickets = cur.fetchall()
        
        # Obtener datos para filtros
        cur.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
        departamentos = cur.fetchall()
        
        cur.execute("SELECT id, nombre FROM tipologias ORDER BY nombre")
        tipologias = cur.fetchall()
        
        cur.close()
        
        return render_template('lista_tickets.html', 
                             tickets=tickets, 
                             departamentos=departamentos,
                             tipologias=tipologias)
    
    except Exception as e:
        return render_template('lista_tickets.html', 
                             error=f"Error al cargar tickets: {str(e)}", 
                             tickets=[], 
                             departamentos=[], 
                             tipologias=[])

# API para obtener detalles completos de un ticket
@app.route('/api/ticket/<int:ticket_id>')
def api_ticket_detalles(ticket_id):
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
            u.rol as usuario_rol,
            t.mando as mando_nombre
        FROM tickets t
        LEFT JOIN departamentos d ON t.departamento_id = d.id
        LEFT JOIN municipios m ON t.municipio_id = m.id
        LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
        LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
        LEFT JOIN usuarios u ON t.usuario_id = u.id
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

if __name__ == '__main__':
    app.secret_key = '1234'
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

