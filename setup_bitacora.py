#!/usr/bin/env python3
"""
Script para crear la tabla de bitácora usando la misma configuración de la aplicación
"""

import sys
import os

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

from flask import Flask
import config

def crear_tabla_bitacora():
    """Crear la tabla de bitácora en la base de datos"""
    
    # Crear aplicación Flask temporalmente
    app = Flask(__name__)
    
    # Inicializar configuración
    config.init_app(app)
    
    with app.app_context():
        cur = config.mysql.connection.cursor()
        
        try:
            print("Creando tabla de bitácora...")
            
            # Script SQL para crear la tabla
            sql_create_table = """
            CREATE TABLE IF NOT EXISTS bitacora (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                usuario_nombre VARCHAR(100) NOT NULL,
                accion VARCHAR(255) NOT NULL,
                modulo VARCHAR(100) NOT NULL,
                descripcion TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                datos_anteriores JSON,
                datos_nuevos JSON,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_fecha_hora (fecha_hora),
                INDEX idx_modulo (modulo),
                INDEX idx_accion (accion),
                
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cur.execute(sql_create_table)
            print("✓ Tabla 'bitacora' creada exitosamente")
            
            # Agregar comentario a la tabla
            cur.execute("ALTER TABLE bitacora COMMENT = 'Registro de todas las actividades realizadas por usuarios del sistema';")
            print("✓ Comentario agregado a la tabla")
            
            # Insertar registro inicial si hay usuarios
            cur.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cur.fetchone()['total']
            
            if total_usuarios > 0:
                cur.execute("SELECT id, usuario FROM usuarios LIMIT 1")
                primer_usuario = cur.fetchone()
                
                if primer_usuario:
                    cur.execute("""
                        INSERT INTO bitacora (usuario_id, usuario_nombre, accion, modulo, descripcion, ip_address) 
                        VALUES (%s, %s, 'SYSTEM_SETUP', 'Sistema', 'Configuración inicial del módulo de bitácora', '127.0.0.1')
                    """, (primer_usuario['id'], primer_usuario['usuario']))
                    print(f"✓ Registro inicial creado para usuario: {primer_usuario['usuario']}")
            
            # Confirmar cambios
            config.mysql.connection.commit()
            print("✓ Cambios confirmados en la base de datos")
            
            # Verificar que la tabla existe
            cur.execute("SHOW TABLES LIKE 'bitacora'")
            if cur.fetchone():
                print("✓ Verificación exitosa: La tabla 'bitacora' existe")
                
                # Mostrar estructura de la tabla
                cur.execute("DESCRIBE bitacora")
                columnas = cur.fetchall()
                print("\n📋 Estructura de la tabla 'bitacora':")
                for columna in columnas:
                    print(f"  - {columna['Field']}: {columna['Type']}")
            else:
                print("❌ Error: La tabla no fue creada correctamente")
                
        except Exception as e:
            print(f"❌ Error al crear la tabla: {e}")
            config.mysql.connection.rollback()
        finally:
            cur.close()

if __name__ == "__main__":
    print("=== Configuración del Módulo de Bitácora ===\n")
    crear_tabla_bitacora()
    print("\n=== Configuración completada ===")