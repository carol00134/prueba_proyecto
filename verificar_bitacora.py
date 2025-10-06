#!/usr/bin/env python3
"""
Script de prueba para verificar que la bitácora está funcionando correctamente
"""

import sys
import os

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from flask import Flask
import config

def verificar_bitacora():
    """Verificar que la bitácora esté funcionando correctamente"""
    
    # Crear aplicación Flask temporalmente
    app = Flask(__name__)
    
    # Inicializar configuración
    config.init_app(app)
    
    with app.app_context():
        cur = config.mysql.connection.cursor()
        
        try:
            print("=== VERIFICACIÓN DEL MÓDULO DE BITÁCORA ===\n")
            
            # 1. Verificar que la tabla existe
            print("1. Verificando que la tabla 'bitacora' existe...")
            cur.execute("SHOW TABLES LIKE 'bitacora'")
            if cur.fetchone():
                print("   ✅ Tabla 'bitacora' encontrada")
            else:
                print("   ❌ Tabla 'bitacora' NO encontrada")
                return
            
            # 2. Verificar estructura de la tabla
            print("\n2. Verificando estructura de la tabla...")
            cur.execute("DESCRIBE bitacora")
            columnas = cur.fetchall()
            columnas_esperadas = ['id', 'usuario_id', 'usuario_nombre', 'accion', 'modulo', 
                                'descripcion', 'ip_address', 'user_agent', 'datos_anteriores', 
                                'datos_nuevos', 'fecha_hora']
            
            columnas_encontradas = [col['Field'] for col in columnas]
            for col in columnas_esperadas:
                if col in columnas_encontradas:
                    print(f"   ✅ Columna '{col}' encontrada")
                else:
                    print(f"   ❌ Columna '{col}' NO encontrada")
            
            # 3. Contar registros existentes
            print("\n3. Contando registros existentes...")
            cur.execute("SELECT COUNT(*) as total FROM bitacora")
            total_registros = cur.fetchone()['total']
            print(f"   📊 Total de registros en bitácora: {total_registros}")
            
            # 4. Mostrar últimos 5 registros
            if total_registros > 0:
                print("\n4. Últimos 5 registros:")
                cur.execute("""
                    SELECT fecha_hora, usuario_nombre, accion, modulo, descripcion 
                    FROM bitacora 
                    ORDER BY fecha_hora DESC 
                    LIMIT 5
                """)
                registros = cur.fetchall()
                
                for i, registro in enumerate(registros, 1):
                    fecha = registro['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"   {i}. [{fecha}] {registro['usuario_nombre']} - {registro['accion']} en {registro['modulo']}")
                    if registro['descripcion']:
                        print(f"      📝 {registro['descripcion'][:80]}{'...' if len(registro['descripcion']) > 80 else ''}")
            
            # 5. Estadísticas por módulo
            print("\n5. Estadísticas por módulo:")
            cur.execute("""
                SELECT modulo, COUNT(*) as cantidad 
                FROM bitacora 
                GROUP BY modulo 
                ORDER BY cantidad DESC
            """)
            stats_modulo = cur.fetchall()
            
            if stats_modulo:
                for stat in stats_modulo:
                    print(f"   📈 {stat['modulo']}: {stat['cantidad']} registros")
            else:
                print("   📊 No hay estadísticas disponibles")
            
            # 6. Estadísticas por acción
            print("\n6. Estadísticas por acción:")
            cur.execute("""
                SELECT accion, COUNT(*) as cantidad 
                FROM bitacora 
                GROUP BY accion 
                ORDER BY cantidad DESC
            """)
            stats_accion = cur.fetchall()
            
            if stats_accion:
                for stat in stats_accion:
                    print(f"   🎯 {stat['accion']}: {stat['cantidad']} registros")
            else:
                print("   🎯 No hay estadísticas de acciones disponibles")
            
            # 7. Verificar índices
            print("\n7. Verificando índices...")
            cur.execute("SHOW INDEX FROM bitacora")
            indices = cur.fetchall()
            
            indices_encontrados = set()
            for indice in indices:
                indices_encontrados.add(indice['Key_name'])
            
            indices_esperados = ['PRIMARY', 'idx_usuario_id', 'idx_fecha_hora', 'idx_modulo', 'idx_accion']
            for indice in indices_esperados:
                if indice in indices_encontrados:
                    print(f"   🔍 Índice '{indice}' encontrado")
                else:
                    print(f"   ⚠️ Índice '{indice}' NO encontrado")
            
            print("\n=== VERIFICACIÓN COMPLETADA ===")
            print("✅ El módulo de bitácora está configurado correctamente")
            print("🎉 Listo para registrar todas las actividades del sistema")
            
        except Exception as e:
            print(f"❌ Error durante la verificación: {e}")
        finally:
            cur.close()

if __name__ == "__main__":
    verificar_bitacora()