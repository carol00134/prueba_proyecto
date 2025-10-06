#!/usr/bin/env python3
"""
Script para probar la funcionalidad de edición de cámaras
"""

import pymysql
from config import MYSQL_CONFIG
import json

def test_edicion_camaras():
    """Prueba la funcionalidad de edición de cámaras"""
    try:
        # Conectar a la base de datos
        config = MYSQL_CONFIG.copy()
        config['cursorclass'] = pymysql.cursors.DictCursor
        connection = pymysql.connect(**config)
        
        with connection:
            with connection.cursor() as cursor:
                print("🔍 DIAGNÓSTICO DE EDICIÓN DE CÁMARAS")
                print("=" * 50)
                
                # 1. Listar cámaras disponibles
                print("\n1️⃣ Cámaras disponibles para editar:")
                cursor.execute("""
                    SELECT id_camaras, nombre, correo, estado, regional, latitud, longitud
                    FROM camaras 
                    ORDER BY id_camaras
                    LIMIT 5
                """)
                
                camaras = cursor.fetchall()
                
                if len(camaras) == 0:
                    print("❌ No hay cámaras en la base de datos")
                    return
                
                for i, camara in enumerate(camaras, 1):
                    print(f"  {i}. ID: {camara['id_camaras']}")
                    print(f"     Nombre: {camara['nombre']}")
                    print(f"     Estado: {camara['estado']}")
                    print(f"     Coordenadas: ({camara['latitud']}, {camara['longitud']})")
                    print("-" * 30)
                
                # 2. Probar obtener datos de la primera cámara para edición
                primera_camara = camaras[0]
                id_test = primera_camara['id_camaras']
                
                print(f"\n2️⃣ Probando obtener datos de cámara '{id_test}' para edición:")
                
                # Simular la consulta que hace el endpoint /api/camara/<id>
                cursor.execute("""
                    SELECT c.id_camaras, c.correo, c.nombre, c.estado, c.regional,
                           c.fecha_creacion, c.fecha_ultima_modificacion, c.cambio_password,
                           c.usuario_id, c.latitud, c.longitud,
                           u.nombre as usuario_nombre
                    FROM camaras c
                    LEFT JOIN usuarios u ON c.usuario_id = u.id
                    WHERE c.id_camaras = %s
                """, (id_test,))
                
                camara_detalle = cursor.fetchone()
                
                if camara_detalle:
                    print("✅ Datos obtenidos correctamente:")
                    response_data = {
                        'success': True,
                        'camara': {
                            'id_camaras': camara_detalle['id_camaras'],
                            'correo': camara_detalle['correo'],
                            'nombre': camara_detalle['nombre'],
                            'estado': camara_detalle['estado'],
                            'regional': camara_detalle['regional'],
                            'fecha_creacion': camara_detalle['fecha_creacion'].strftime('%Y-%m-%d') if camara_detalle['fecha_creacion'] else '',
                            'usuario_id': camara_detalle['usuario_id'],
                            'latitud': float(camara_detalle['latitud']) if camara_detalle['latitud'] else '',
                            'longitud': float(camara_detalle['longitud']) if camara_detalle['longitud'] else '',
                            'usuario_nombre': camara_detalle['usuario_nombre']
                        }
                    }
                    print(json.dumps(response_data, indent=2, ensure_ascii=False, default=str))
                else:
                    print("❌ No se encontraron datos para la cámara")
                
                # 3. Verificar tabla de usuarios
                print(f"\n3️⃣ Verificando tabla de usuarios:")
                cursor.execute("SELECT id, nombre FROM usuarios LIMIT 3")
                usuarios = cursor.fetchall()
                
                if len(usuarios) > 0:
                    print(f"✅ {len(usuarios)} usuarios encontrados:")
                    for usuario in usuarios:
                        print(f"   ID: {usuario['id']}, Nombre: {usuario['nombre']}")
                else:
                    print("⚠️ No hay usuarios en la tabla (puede afectar el dropdown)")
                
                print(f"\n🎯 RESUMEN:")
                print(f"   - Cámaras disponibles: {len(camaras)}")
                print(f"   - Primera cámara ID: {id_test}")
                print(f"   - Datos de edición: {'✅ OK' if camara_detalle else '❌ Error'}")
                print(f"   - Usuarios disponibles: {len(usuarios)}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error en diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_edicion_camaras()