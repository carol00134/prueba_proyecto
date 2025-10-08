from flask import render_template, jsonify
from config import mysql
from utils.auth_utils import role_required, login_required

class MapasController:
    @staticmethod
    @role_required('administrador', 'operador')
    def mapas():
        """Handle maps page"""
        return render_template('mapas.html')
    
    @staticmethod
    @role_required('administrador', 'operador')
    def get_puntos_geograficos():
        """Get geographic points for map display"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener puntos geográficos con coordenadas
            cur.execute("""
                SELECT 
                    p.id,
                    p.nombre,
                    p.descripcion,
                    p.direccion,
                    ST_X(p.location) as longitud,
                    ST_Y(p.location) as latitud,
                    d.nombre as departamento,
                    m.nombre as municipio,
                    p.fecha_registro,
                    p.activo
                FROM puntos_geograficos p
                LEFT JOIN departamentos d ON p.departamento_id = d.id
                LEFT JOIN municipios m ON p.municipio_id = m.id
                WHERE p.activo = 1
                ORDER BY p.nombre
            """)
            
            puntos = cur.fetchall()
            
            # Convertir a formato GeoJSON
            features = []
            for punto in puntos:
                if punto['latitud'] and punto['longitud']:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(punto['longitud']), float(punto['latitud'])]
                        },
                        "properties": {
                            "id": punto['id'],
                            "nombre": punto['nombre'],
                            "descripcion": punto['descripcion'] or '',
                            "direccion": punto['direccion'] or '',
                            "departamento": punto['departamento'] or '',
                            "municipio": punto['municipio'] or '',
                            "fecha_registro": punto['fecha_registro'].isoformat() if punto['fecha_registro'] else '',
                            "tipo": "punto_geografico"
                        }
                    }
                    features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            cur.close()
            return jsonify(geojson)
            
        except Exception as e:
            print(f"Error al obtener puntos geográficos: {str(e)}")
            return jsonify({"type": "FeatureCollection", "features": []})
    
    @staticmethod
    @role_required('administrador', 'operador')
    def get_camaras():
        """Get cameras data for map display"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener cámaras con coordenadas (todas las que tienen coordenadas)
            cur.execute("""
                SELECT 
                    id_camaras,
                    nombre,
                    correo,
                    estado,
                    regional,
                    fecha_creacion,
                    latitud,
                    longitud
                FROM camaras
                WHERE latitud IS NOT NULL AND longitud IS NOT NULL
                ORDER BY nombre
            """)
            
            camaras = cur.fetchall()
            
            # Convertir a formato GeoJSON
            features = []
            for camara in camaras:
                if camara['latitud'] and camara['longitud']:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(camara['longitud']), float(camara['latitud'])]
                        },
                        "properties": {
                            "id": camara['id_camaras'],
                            "nombre": camara['nombre'],
                            "correo": camara['correo'],
                            "estado": camara['estado'],
                            "regional": camara['regional'] or '',
                            "fecha_creacion": camara['fecha_creacion'].isoformat() if camara['fecha_creacion'] else '',
                            "tipo": "camara"
                        }
                    }
                    features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            cur.close()
            return jsonify(geojson)
            
        except Exception as e:
            print(f"Error al obtener cámaras: {str(e)}")
            return jsonify({"type": "FeatureCollection", "features": []})
    
    @staticmethod
    @role_required('administrador', 'operador')
    def get_tickets():
        """Get tickets data for map display with emergency types"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener tickets con coordenadas, tipologías y subtipologías
            cur.execute("""
                SELECT 
                    t.id,
                    t.fecha_hora,
                    t.regional,
                    t.descripcion,
                    ST_X(t.location) as longitud,
                    ST_Y(t.location) as latitud,
                    d.nombre as departamento,
                    m.nombre as municipio,
                    tip.id as tipologia_id,
                    tip.nombre as tipologia_nombre,
                    stip.id as subtipologia_id,
                    stip.nombre as subtipologia_nombre,
                    u.nombre as usuario_nombre
                FROM tickets t
                LEFT JOIN departamentos d ON t.departamento_id = d.id
                LEFT JOIN municipios m ON t.municipio_id = m.id
                LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
                LEFT JOIN subtipologias stip ON t.subtipologia_id = stip.id
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE ST_X(t.location) != 0 AND ST_Y(t.location) != 0
                ORDER BY t.fecha_hora DESC
            """)
            
            tickets = cur.fetchall()
            
            # Convertir a formato GeoJSON
            features = []
            for ticket in tickets:
                if ticket['latitud'] and ticket['longitud']:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(ticket['longitud']), float(ticket['latitud'])]
                        },
                        "properties": {
                            "id": ticket['id'],
                            "fecha_hora": ticket['fecha_hora'].isoformat() if ticket['fecha_hora'] else '',
                            "regional": ticket['regional'] or '',
                            "descripcion": ticket['descripcion'] or '',
                            "departamento": ticket['departamento'] or '',
                            "municipio": ticket['municipio'] or '',
                            "tipologia_id": ticket['tipologia_id'],
                            "tipologia_nombre": ticket['tipologia_nombre'] or '',
                            "subtipologia_id": ticket['subtipologia_id'],
                            "subtipologia_nombre": ticket['subtipologia_nombre'] or '',
                            "usuario_nombre": ticket['usuario_nombre'] or '',
                            "tipo": "ticket"
                        }
                    }
                    features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            cur.close()
            return jsonify(geojson)
            
        except Exception as e:
            print(f"Error al obtener tickets: {str(e)}")
            return jsonify({"type": "FeatureCollection", "features": []})