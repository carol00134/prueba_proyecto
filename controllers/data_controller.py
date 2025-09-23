from flask import jsonify
from config import mysql

class DataController:
    @staticmethod
    def poblar_datos():
        """Populate initial data - REMOVE IN PRODUCTION"""
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