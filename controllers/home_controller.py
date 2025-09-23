from flask import render_template, redirect, session
from config import mysql

class HomeController:
    @staticmethod
    def home():
        """Handle home page with dashboard statistics"""
        if 'usuario' in session:
            cur = mysql.connection.cursor()
            
            # Contar usuarios activos
            cur.execute("SELECT COUNT(*) AS activos FROM usuarios WHERE activo = 1")
            usuarios_activos = cur.fetchone()['activos']
            
            # Contar cámaras activas
            cur.execute("SELECT COUNT(*) AS activas FROM camaras WHERE estado = 1")
            camaras_activas = cur.fetchone()['activas']
            
            # Contar tickets totales (como no hay estado, contamos todos)
            cur.execute("SELECT COUNT(*) AS total_tickets FROM tickets")
            tickets_nuevos = cur.fetchone()['total_tickets']
            
            # Contar puntos geográficos registrados
            cur.execute("SELECT COUNT(*) AS total_puntos FROM puntos_geograficos")
            puntos_geograficos = cur.fetchone()['total_puntos']
            
            # Obtener hora actual del servidor
            cur.execute("SELECT NOW() as hora_actual")
            hora_actual = cur.fetchone()['hora_actual']
            
            # Verificar conectividad de la base de datos (si llegamos aquí, está conectada)
            estado_bd = "En línea"
            
            cur.close()
            
            return render_template('index.html', 
                                 usuarios_activos=usuarios_activos,
                                 camaras_activas=camaras_activas,
                                 tickets_nuevos=tickets_nuevos,
                                 puntos_geograficos=puntos_geograficos,
                                 hora_actual=hora_actual,
                                 estado_bd=estado_bd)
        else:
            return redirect('/login')