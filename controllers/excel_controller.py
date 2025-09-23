import panda as pd

@app.route('/subir_excel', methods=['POST'] )
def cargar_archivos ():
    print("Cargando Datos...")
    return render_template("tickets.html")
    
