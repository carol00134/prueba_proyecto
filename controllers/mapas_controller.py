from flask import render_template

class MapasController:
    @staticmethod
    def mapas():
        """Handle maps page"""
        return render_template('mapas.html')