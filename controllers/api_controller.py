from flask import request, jsonify
from config import mysql

class ApiController:
    @staticmethod
    def api_puntos():
        """API endpoint for points with filters"""
        municipio = request.args.get('municipio', '')
        tipologia = request.args.get('tipologia', '')
        fecha = request.args.get('fecha', '')
        cur = mysql.connection.cursor()
        query = '''
            SELECT t.id, m.nombre AS municipio, tp.nombre AS tipologia, t.fecha_hora,
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
            query += " AND DATE(t.fecha_hora) = %s"
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
                'fecha': r['fecha_hora'],
                'lat': r['lat'],
                'lng': r['lng']
            })
        return jsonify(puntos)

    @staticmethod
    def api_usuarios_activos():
        """API endpoint for active users count"""
        cur = mysql.connection.cursor()
        # Contar todos los usuarios registrados
        cur.execute('SELECT COUNT(*) AS activos FROM usuarios')
        activos = cur.fetchone()['activos']
        cur.close()
        return jsonify({'activos': activos})

    @staticmethod
    def api_municipios(departamento_id):
        """API endpoint to get municipalities by department"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre FROM municipios WHERE departamento_id = %s ORDER BY nombre", 
                    (departamento_id,))
        municipios = cur.fetchall()
        cur.close()
        return jsonify(municipios)

    @staticmethod
    def api_subtipologias(tipologia_id):
        """API endpoint to get subtypologies by typology"""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre FROM subtipologias WHERE tipologia_id = %s ORDER BY nombre", 
                    (tipologia_id,))
        subtipologias = cur.fetchall()
        cur.close()
        return jsonify(subtipologias)
    
    @staticmethod
    def api_camara_detalles(id_camaras):
        """API endpoint to get camera details"""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.*, u.nombre as usuario_nombre, r.nombre as rol_nombre
            FROM camaras c
            LEFT JOIN usuarios u ON c.usuario_id = u.id
            LEFT JOIN roles r ON c.rol_id = r.id
            WHERE c.id_camaras = %s
        """, (id_camaras,))
        camara = cur.fetchone()
        cur.close()
        
        if camara:
            return jsonify({
                'success': True,
                'camara': dict(camara)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Cámara no encontrada'
            })