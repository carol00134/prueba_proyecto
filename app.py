from flask import Flask
from flask import render_template, redirect, request, Response, session, jsonify
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
        cur.execute("SELECT COUNT(*) AS activos FROM usuarios WHERE rol IS NOT NULL AND rol != '';")
        activos = cur.fetchone()['activos']
        cur.close()
        return render_template('index.html', usuarios_activos=activos)
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['contrasena'], password):
            session['usuario'] = username
            return redirect('/')
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')
 
    
@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    cur = mysql.connection.cursor()
    usuario_editar = None
    if request.method == 'POST':
        accion = request.form.get('accion')
        username = request.form.get('username')
        password = request.form.get('password')
        rol = request.form.get('rol')
        if accion == 'agregar':
            if password:
                hashed_password = generate_password_hash(password)
            else:
                hashed_password = generate_password_hash('')
            cur.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (%s, %s, %s)", (username, hashed_password, rol))
            mysql.connection.commit()
        elif accion == 'editar':
            hashed_password = generate_password_hash(password)
            cur.execute("UPDATE usuarios SET contrasena = %s, rol = %s WHERE usuario = %s", (hashed_password, rol, username))
            mysql.connection.commit()
        elif accion == 'eliminar':
            cur.execute("DELETE FROM usuarios WHERE usuario = %s", (username,))
            mysql.connection.commit()
        elif accion == 'mostrar_editar' or accion == 'agregar':
            cur.execute("SELECT usuario, rol FROM usuarios WHERE usuario = %s", (username,))
            usuario_editar = cur.fetchone()
    cur.execute("SELECT usuario, rol FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios, usuario_editar=usuario_editar)


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
        cur.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        return redirect('/login')
    return render_template('login.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/puntoGeografico')
def puntoGeografico():
    return render_template('puntoGeografico.html')



from flask import jsonify

@app.route('/api/puntos')
def api_puntos():
    municipio = request.args.get('municipio', '')
    tipologia = request.args.get('tipologia', '')
    fecha = request.args.get('fecha', '')
    cur = mysql.connection.cursor()
    query = "SELECT municipio, tipologia, fecha, coordenada FROM puntos_geograficos WHERE 1=1"
    params = []
    if municipio:
        query += " AND municipio LIKE %s"
        params.append(f"%{municipio}%")
    if tipologia:
        query += " AND tipologia LIKE %s"
        params.append(f"%{tipologia}%")
    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)
    cur.execute(query, params)
    resultados = cur.fetchall()
    cur.close()
    puntos = []
    for r in resultados:
        try:
            lat, lng = map(float, r['coordenada'].split(','))
        except Exception:
            lat, lng = None, None
        puntos.append({
            'municipio': r['municipio'],
            'tipologia': r['tipologia'],
            'fecha': r['fecha'],
            'lat': lat,
            'lng': lng
        })
    return jsonify(puntos)

@app.route('/api/usuarios_activos')
def api_usuarios_activos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS activos FROM usuarios WHERE rol IS NOT NULL AND rol != '';")
    activos = cur.fetchone()['activos']
    cur.close()
    return jsonify({'activos': activos})
    # ...existing code...

if __name__ == '__main__':
    app.secret_key = '1234'
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

