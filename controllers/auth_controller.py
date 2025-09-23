from flask import render_template, redirect, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import mysql

class AuthController:
    @staticmethod
    def login():
        """Handle user login"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return render_template('login.html', error='Por favor complete todos los campos')
            
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT u.*
                FROM usuarios u
                WHERE u.usuario = %s
            """, (username,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                if check_password_hash(user['contraseña'], password):
                    session['usuario'] = username
                    return redirect('/')
                else:
                    return render_template('login.html', error='Contraseña incorrecta')
            else:
                return render_template('login.html', error='Usuario no encontrado')
        return render_template('login.html')

    @staticmethod
    def register():
        """Handle user registration"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            hashed_password = generate_password_hash(password)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (usuario, contraseña) VALUES (%s, %s)", (username, hashed_password))
            mysql.connection.commit()
            cur.close()
            return redirect('/login')
        return render_template('login.html')

    @staticmethod
    def logout():
        """Handle user logout"""
        session.pop('usuario', None)
        return redirect('/login')