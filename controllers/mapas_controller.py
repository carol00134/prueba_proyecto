from flask import render_template, jsonify
from config import mysql

class MapasController:
    @staticmethod
    def mapas():
        """Handle maps page"""
        return render_template('mapas.html')
    
    @staticmethod
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
    def get_camaras():
        """Get cameras data for map display"""
        try:
            cur = mysql.connection.cursor()
            
            # Obtener cámaras activas con coordenadas
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
                WHERE estado = 1 AND latitud IS NOT NULL AND longitud IS NOT NULL
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