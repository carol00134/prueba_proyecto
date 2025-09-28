from config import mysql

try:
    cur = mysql.connection.cursor()
    
    # Verificar departamentos
    cur.execute('SELECT COUNT(*) as total FROM departamentos')
    dep_count = cur.fetchone()
    print(f'Departamentos en BD: {dep_count["total"] if dep_count else 0}')
    
    # Verificar municipios
    cur.execute('SELECT COUNT(*) as total FROM municipios')
    mun_count = cur.fetchone()
    print(f'Municipios en BD: {mun_count["total"] if mun_count else 0}')
    
    # Verificar algunos municipios de ejemplo
    cur.execute('SELECT m.id, m.nombre, d.nombre as departamento FROM municipios m LEFT JOIN departamentos d ON m.departamento_id = d.id LIMIT 5')
    municipios = cur.fetchall()
    print('Ejemplos de municipios:')
    for m in municipios:
        print(f'  - {m["nombre"]} (Dept: {m["departamento"]})')
    
    cur.close()
    print('✓ Conexión a BD exitosa')
    
except Exception as e:
    print(f'✗ Error de BD: {e}')