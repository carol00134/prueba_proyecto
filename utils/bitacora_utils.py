"""
Utilidades adicionales para el módulo de bitácora
"""
from controllers.bitacora_controller import BitacoraController
from flask import session
import json

class BitacoraUtils:
    
    @staticmethod
    def registrar_operacion_masiva(accion, modulo, elementos, descripcion_base=""):
        """
        Registrar una operación que afecta múltiples elementos
        
        Args:
            accion (str): Tipo de acción
            modulo (str): Módulo donde se realiza
            elementos (list): Lista de elementos afectados
            descripcion_base (str): Descripción base de la operación
        """
        if 'usuario' not in session:
            return
        
        descripcion = f"{descripcion_base} - Procesados {len(elementos)} elementos"
        
        BitacoraController.registrar_accion(
            accion=accion,
            modulo=modulo,
            descripcion=descripcion,
            datos_nuevos={
                'elementos_procesados': len(elementos),
                'elementos': elementos[:10] if len(elementos) > 10 else elementos  # Limitar a 10 para evitar exceso de datos
            }
        )
    
    @staticmethod
    def registrar_consulta_reporte(modulo, tipo_reporte, filtros=None, total_registros=None):
        """
        Registrar consultas de reportes y exportaciones
        
        Args:
            modulo (str): Módulo donde se genera el reporte
            tipo_reporte (str): Tipo de reporte generado
            filtros (dict): Filtros aplicados al reporte
            total_registros (int): Número de registros en el reporte
        """
        if 'usuario' not in session:
            return
        
        descripcion = f"Generó reporte de {tipo_reporte}"
        if total_registros is not None:
            descripcion += f" con {total_registros} registros"
        
        datos_reporte = {
            'tipo_reporte': tipo_reporte,
            'total_registros': total_registros
        }
        
        if filtros:
            datos_reporte['filtros_aplicados'] = filtros
        
        BitacoraController.registrar_accion(
            accion='REPORT',
            modulo=modulo,
            descripcion=descripcion,
            datos_nuevos=datos_reporte
        )
    
    @staticmethod
    def registrar_error_sistema(modulo, error_tipo, error_descripcion, datos_error=None):
        """
        Registrar errores del sistema para auditoria
        
        Args:
            modulo (str): Módulo donde ocurrió el error
            error_tipo (str): Tipo de error
            error_descripcion (str): Descripción del error
            datos_error (dict): Datos adicionales del error
        """
        if 'usuario' not in session:
            return
        
        BitacoraController.registrar_accion(
            accion='ERROR',
            modulo=modulo,
            descripcion=f"{error_tipo}: {error_descripcion}",
            datos_nuevos=datos_error
        )
    
    @staticmethod
    def registrar_configuracion(modulo, configuracion_cambiada, valor_anterior, valor_nuevo):
        """
        Registrar cambios de configuración del sistema
        
        Args:
            modulo (str): Módulo de configuración
            configuracion_cambiada (str): Nombre de la configuración
            valor_anterior: Valor anterior
            valor_nuevo: Valor nuevo
        """
        if 'usuario' not in session:
            return
        
        BitacoraController.registrar_accion(
            accion='CONFIG_CHANGE',
            modulo=modulo,
            descripcion=f"Cambió configuración: {configuracion_cambiada}",
            datos_anteriores={'configuracion': configuracion_cambiada, 'valor': valor_anterior},
            datos_nuevos={'configuracion': configuracion_cambiada, 'valor': valor_nuevo}
        )
    
    @staticmethod
    def obtener_resumen_actividad_usuario(usuario_nombre, dias=7):
        """
        Obtener resumen de actividad de un usuario específico
        
        Args:
            usuario_nombre (str): Nombre del usuario
            dias (int): Número de días hacia atrás
            
        Returns:
            dict: Resumen de actividad
        """
        from config import mysql
        
        cur = mysql.connection.cursor()
        
        # Actividad por módulo
        cur.execute("""
            SELECT modulo, COUNT(*) as cantidad
            FROM bitacora 
            WHERE usuario_nombre = %s 
            AND fecha_hora >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY modulo
            ORDER BY cantidad DESC
        """, (usuario_nombre, dias))
        actividad_modulos = cur.fetchall()
        
        # Actividad por acción
        cur.execute("""
            SELECT accion, COUNT(*) as cantidad
            FROM bitacora 
            WHERE usuario_nombre = %s 
            AND fecha_hora >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY accion
            ORDER BY cantidad DESC
        """, (usuario_nombre, dias))
        actividad_acciones = cur.fetchall()
        
        # Total de actividades
        cur.execute("""
            SELECT COUNT(*) as total
            FROM bitacora 
            WHERE usuario_nombre = %s 
            AND fecha_hora >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (usuario_nombre, dias))
        total_actividades = cur.fetchone()['total']
        
        # Última actividad
        cur.execute("""
            SELECT fecha_hora, accion, modulo, descripcion
            FROM bitacora 
            WHERE usuario_nombre = %s 
            ORDER BY fecha_hora DESC
            LIMIT 1
        """, (usuario_nombre,))
        ultima_actividad = cur.fetchone()
        
        cur.close()
        
        return {
            'usuario': usuario_nombre,
            'periodo_dias': dias,
            'total_actividades': total_actividades,
            'actividad_por_modulo': actividad_modulos,
            'actividad_por_accion': actividad_acciones,
            'ultima_actividad': dict(ultima_actividad) if ultima_actividad else None
        }
    
    @staticmethod
    def limpiar_bitacora_antigua(dias_antigüedad=90):
        """
        Limpiar registros antiguos de bitácora para mantener rendimiento
        
        Args:
            dias_antigüedad (int): Eliminar registros más antiguos que estos días
            
        Returns:
            int: Número de registros eliminados
        """
        from config import mysql
        
        if 'usuario' not in session:
            return 0
        
        cur = mysql.connection.cursor()
        
        # Contar registros a eliminar
        cur.execute("""
            SELECT COUNT(*) as total
            FROM bitacora 
            WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_antigüedad,))
        registros_a_eliminar = cur.fetchone()['total']
        
        # Eliminar registros antiguos
        cur.execute("""
            DELETE FROM bitacora 
            WHERE fecha_hora < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (dias_antigüedad,))
        
        mysql.connection.commit()
        cur.close()
        
        # Registrar la limpieza
        BitacoraController.registrar_accion(
            accion='MAINTENANCE',
            modulo='Sistema',
            descripcion=f'Limpieza de bitácora: eliminados {registros_a_eliminar} registros antiguos (>{dias_antigüedad} días)',
            datos_nuevos={
                'registros_eliminados': registros_a_eliminar,
                'dias_antiguedad': dias_antigüedad
            }
        )
        
        return registros_a_eliminar