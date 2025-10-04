#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y configurar datos de prueba para el mapa
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import mysql
from flask import Flask

def crear_datos_prueba():
    """Crear datos de prueba para el mapa si no existen"""
    
    app = Flask(__name__)
    
    # Configurar la aplicación
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'  # Cambiar según tu configuración
    app.config['MYSQL_PASSWORD'] = ''  # Cambiar según tu configuración
    app.config['MYSQL_DB'] = 'proyecto'  # Cambiar según tu base de datos
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql.init_app(app)
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("Verificando datos existentes...")
            
            # Verificar departamentos
            cur.execute("SELECT COUNT(*) as count FROM departamentos")
            dept_count = cur.fetchone()['count']
            print(f"Departamentos existentes: {dept_count}")
            
            # Verificar municipios
            cur.execute("SELECT COUNT(*) as count FROM municipios")
            mun_count = cur.fetchone()['count']
            print(f"Municipios existentes: {mun_count}")
            
            # Verificar puntos geográficos
            cur.execute("SELECT COUNT(*) as count FROM puntos_geograficos")
            puntos_count = cur.fetchone()['count']
            print(f"Puntos geográficos existentes: {puntos_count}")
            
            # Verificar cámaras
            cur.execute("SELECT COUNT(*) as count FROM camaras")
            camaras_count = cur.fetchone()['count']
            print(f"Cámaras existentes: {camaras_count}")
            
            # Si no hay datos, crear algunos de prueba
            if dept_count == 0:
                print("Creando departamentos de prueba...")
                departamentos = [
                    "Francisco Morazán",
                    "Cortés",
                    "Atlántida",
                    "Yoro",
                    "Comayagua"
                ]
                
                for dept in departamentos:
                    cur.execute("INSERT INTO departamentos (nombre) VALUES (%s)", (dept,))
                
                mysql.connection.commit()
                print("Departamentos creados.")
            
            # Obtener IDs de departamentos
            cur.execute("SELECT id, nombre FROM departamentos LIMIT 5")
            departamentos = cur.fetchall()
            
            if mun_count == 0 and len(departamentos) > 0:
                print("Creando municipios de prueba...")
                municipios = [
                    ("Tegucigalpa", departamentos[0]['id']),
                    ("San Pedro Sula", departamentos[1]['id'] if len(departamentos) > 1 else departamentos[0]['id']),
                    ("La Ceiba", departamentos[2]['id'] if len(departamentos) > 2 else departamentos[0]['id']),
                    ("Comayagüela", departamentos[0]['id']),
                    ("Choloma", departamentos[1]['id'] if len(departamentos) > 1 else departamentos[0]['id'])
                ]
                
                for mun_nombre, dept_id in municipios:
                    cur.execute("INSERT INTO municipios (nombre, departamento_id) VALUES (%s, %s)", 
                              (mun_nombre, dept_id))
                
                mysql.connection.commit()
                print("Municipios creados.")
            
            # Obtener IDs de municipios
            cur.execute("SELECT id, nombre, departamento_id FROM municipios LIMIT 5")
            municipios = cur.fetchall()
            
            if puntos_count == 0 and len(municipios) > 0:
                print("Creando puntos geográficos de prueba...")
                puntos = [
                    ("Centro de Tegucigalpa", "Centro histórico de la capital", municipios[0]['departamento_id'], municipios[0]['id'], "Avenida Cervantes", 14.0723, -87.1921),
                    ("Parque Central SPS", "Parque central de San Pedro Sula", municipios[1]['departamento_id'] if len(municipios) > 1 else municipios[0]['departamento_id'], municipios[1]['id'] if len(municipios) > 1 else municipios[0]['id'], "Parque Central", 15.5041, -88.0250),
                    ("Puerto de La Ceiba", "Puerto principal de La Ceiba", municipios[2]['departamento_id'] if len(municipios) > 2 else municipios[0]['departamento_id'], municipios[2]['id'] if len(municipios) > 2 else municipios[0]['id'], "Zona portuaria", 15.7597, -86.7822),
                    ("Universidad Nacional", "Campus UNAH Tegucigalpa", municipios[0]['departamento_id'], municipios[0]['id'], "Ciudad Universitaria", 14.0839, -87.1712),
                    ("Aeropuerto Toncontín", "Aeropuerto Internacional Toncontín", municipios[0]['departamento_id'], municipios[0]['id'], "Zona aeroportuaria", 14.0608, -87.2172)
                ]
                
                for nombre, descripcion, dept_id, mun_id, direccion, lat, lng in puntos:
                    point_wkt = f"POINT({lng} {lat})"
                    cur.execute("""
                        INSERT INTO puntos_geograficos 
                        (nombre, descripcion, departamento_id, municipio_id, direccion, location) 
                        VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s))
                    """, (nombre, descripcion, dept_id, mun_id, direccion, point_wkt))
                
                mysql.connection.commit()
                print("Puntos geográficos creados.")
            
            if camaras_count == 0:
                print("Creando cámaras de prueba...")
                camaras = [
                    ("CAM001", "admin@sistema.hn", "Cámara Centro Tegucigalpa", True, "Francisco Morazán"),
                    ("CAM002", "operador@sistema.hn", "Cámara Parque Central SPS", True, "Cortés"),
                    ("CAM003", "seguridad@sistema.hn", "Cámara Puerto La Ceiba", True, "Atlántida"),
                    ("CAM004", "monitor@sistema.hn", "Cámara UNAH", True, "Francisco Morazán"),
                    ("CAM005", "vigilancia@sistema.hn", "Cámara Aeropuerto", True, "Francisco Morazán")
                ]
                
                for id_cam, correo, nombre, estado, regional in camaras:
                    cur.execute("""
                        INSERT INTO camaras 
                        (id_camaras, correo, nombre, estado, regional) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (id_cam, correo, nombre, estado, regional))
                
                mysql.connection.commit()
                print("Cámaras creadas.")
            
            print("\n¡Configuración completada!")
            print("Ahora puedes acceder a /mapas para ver el mapa con los datos.")
            
            cur.close()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Verifica tu configuración de base de datos en config.py")

if __name__ == "__main__":
    crear_datos_prueba()