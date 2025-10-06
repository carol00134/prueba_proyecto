from flask import render_template, request, session, jsonify, redirect, url_for
from config import mysql
from datetime import datetime, timedelta
import json

class BitacoraController:
    
    @staticmethod
    def index():
        """Mostrar la página principal de bitácora con filtros"""
        if 'usuario' not in session:
            return redirect('/login')
        
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio', '')
        fecha_fin = request.args.get('fecha_fin', '')
        usuario_filtro = request.args.get('usuario', '')
        modulo_filtro = request.args.get('modulo', '')
        accion_filtro = request.args.get('accion', '')
        page = int(request.args.get('page', 1))
        per_page = 50  # Registros por página
        
        # Construir consulta base
        where_conditions = []
        params = []
        
        if fecha_inicio:
            where_conditions.append("DATE(fecha_hora) >= %s")
            params.append(fecha_inicio)
        
        if fecha_fin:
            where_conditions.append("DATE(fecha_hora) <= %s")
            params.append(fecha_fin)
        
        if usuario_filtro:
            where_conditions.append("usuario_nombre LIKE %s")
            params.append(f"%{usuario_filtro}%")
        
        if modulo_filtro:
            where_conditions.append("modulo = %s")
            params.append(modulo_filtro)
        
        if accion_filtro:
            where_conditions.append("accion = %s")
            params.append(accion_filtro)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        cur = mysql.connection.cursor()
        
        try:
            # Contar total de registros
            count_query = f"SELECT COUNT(*) as total FROM bitacora{where_clause}"
            cur.execute(count_query, params)
            total_records = cur.fetchone()['total']
            
            # Calcular offset
            offset = (page - 1) * per_page
            
            # Obtener registros paginados
            query = f"""
                SELECT * FROM bitacora 
                {where_clause}
                ORDER BY fecha_hora DESC 
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset])
            cur.execute(query, params)
            registros = cur.fetchall()
            
            # Obtener listas para filtros (solo si hay registros)
            usuarios = []
            modulos = []
            acciones = []
            
            if total_records > 0:
                cur.execute("SELECT DISTINCT usuario_nombre FROM bitacora ORDER BY usuario_nombre")
                usuarios = [row['usuario_nombre'] for row in cur.fetchall()]
                
                cur.execute("SELECT DISTINCT modulo FROM bitacora ORDER BY modulo")
                modulos = [row['modulo'] for row in cur.fetchall()]
                
                cur.execute("SELECT DISTINCT accion FROM bitacora ORDER BY accion")
                acciones = [row['accion'] for row in cur.fetchall()]
            
        except Exception as e:
            print(f"Error en consulta de bitácora: {e}")
            registros = []
            usuarios = []
            modulos = []
            acciones = []
            total_records = 0
        finally:
            cur.close()
        
        # Calcular información de paginación
        total_pages = (total_records + per_page - 1) // per_page if total_records > 0 else 1
        
        return render_template('bitacora.html', 
                             registros=registros,
                             usuarios=usuarios,
                             modulos=modulos,
                             acciones=acciones,
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             filters={
                                 'fecha_inicio': fecha_inicio,
                                 'fecha_fin': fecha_fin,
                                 'usuario': usuario_filtro,
                                 'modulo': modulo_filtro,
                                 'accion': accion_filtro
                             })
    
    @staticmethod
    def registrar_accion(accion, modulo, descripcion='', datos_anteriores=None, datos_nuevos=None):
        """
        Registrar una acción en la bitácora
        
        Args:
            accion (str): Tipo de acción (LOGIN, CREATE, UPDATE, DELETE, etc.)
            modulo (str): Módulo donde se realizó la acción
            descripcion (str): Descripción detallada de la acción
            datos_anteriores (dict): Datos antes del cambio (opcional)
            datos_nuevos (dict): Datos después del cambio (opcional)
        """
        if 'usuario' not in session:
            return
        
        cur = None
        try:
            cur = mysql.connection.cursor()
            
            # Obtener información del usuario
            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (session['usuario'],))
            usuario_data = cur.fetchone()
            
            if not usuario_data:
                if cur:
                    cur.close()
                return
            
            usuario_id = usuario_data['id']
            
            # Obtener IP y User Agent
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            # Convertir datos a JSON si existen
            datos_anteriores_json = json.dumps(datos_anteriores, ensure_ascii=False) if datos_anteriores else None
            datos_nuevos_json = json.dumps(datos_nuevos, ensure_ascii=False) if datos_nuevos else None
            
            # Insertar registro en bitácora
            cur.execute("""
                INSERT INTO bitacora 
                (usuario_id, usuario_nombre, accion, modulo, descripcion, 
                 ip_address, user_agent, datos_anteriores, datos_nuevos)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, session['usuario'], accion, modulo, descripcion,
                  ip_address, user_agent, datos_anteriores_json, datos_nuevos_json))
            
            mysql.connection.commit()
            
        except Exception as e:
            print(f"Error al registrar en bitácora: {e}")
            if mysql.connection:
                mysql.connection.rollback()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_detalle(id):
        """Obtener detalle completo de un registro de bitácora"""
        if 'usuario' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM bitacora WHERE id = %s", (id,))
        registro = cur.fetchone()
        cur.close()
        
        if not registro:
            return jsonify({'error': 'Registro no encontrado'}), 404
        
        # Convertir fechas a string para JSON
        if registro['fecha_hora']:
            registro['fecha_hora'] = registro['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Parsear JSON si existe
        if registro['datos_anteriores']:
            registro['datos_anteriores'] = json.loads(registro['datos_anteriores'])
        
        if registro['datos_nuevos']:
            registro['datos_nuevos'] = json.loads(registro['datos_nuevos'])
        
        return jsonify(registro)
