from flask import request, jsonify, session, send_file
import pandas as pd
import io
import datetime
import tempfile
from config import mysql
from controllers.bitacora_controller import BitacoraController
import uuid

class ExcelController:
    
    @staticmethod
    def importar_camaras():
        """
        Importa cámaras desde un archivo Excel
        """
        try:
            print("=== INICIO IMPORTACIÓN CÁMARAS ===")
            
            # Verificar que se envió un archivo
            if 'archivo_excel' not in request.files:
                print("ERROR: No se encontró archivo_excel en request.files")
                return jsonify({
                    'success': False,
                    'message': 'No se seleccionó ningún archivo'
                })
            
            archivo = request.files['archivo_excel']
            print(f"Archivo recibido: {archivo.filename}")
            
            # Verificar que el archivo no esté vacío
            if archivo.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No se seleccionó ningún archivo'
                })
            
            # Verificar extensión del archivo
            extensiones_permitidas = ['.xlsx', '.xls']
            if not any(archivo.filename.lower().endswith(ext) for ext in extensiones_permitidas):
                return jsonify({
                    'success': False,
                    'message': 'Solo se permiten archivos Excel (.xlsx, .xls)'
                })
            
            # Leer el archivo Excel
            try:
                df = pd.read_excel(archivo, engine='openpyxl' if archivo.filename.endswith('.xlsx') else 'xlrd')
                print(f"Archivo leído: {len(df)} filas, Columnas: {list(df.columns)}")
            except Exception as e:
                print(f"ERROR al leer Excel: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Error al leer el archivo Excel: {str(e)}'
                })
            
            # Normalizar nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            print(f"Columnas normalizadas: {list(df.columns)}")
            
            # Mapeo flexible de columnas
            mapeo_columnas = {
                'id': 'id_camaras',
                'id_camara': 'id_camaras',
                'email': 'correo',
                'e-mail': 'correo',
                'mail': 'correo',
                'activo': 'estado',
                'status': 'estado',
                'region': 'regional',
                'latitude': 'latitud',
                'lat': 'latitud',
                'longitude': 'longitud',
                'lng': 'longitud',
                'lon': 'longitud'
            }
            
            # Aplicar mapeo
            for col_original, col_nueva in mapeo_columnas.items():
                if col_original in df.columns:
                    df.rename(columns={col_original: col_nueva}, inplace=True)
                    print(f"Mapeo: {col_original} -> {col_nueva}")
            
            print(f"Columnas finales: {list(df.columns)}")
            
            # Validar columnas requeridas
            columnas_requeridas = ['id_camaras', 'correo', 'nombre']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                mensaje_error = f'Faltan columnas: {", ".join(columnas_faltantes)}. Disponibles: {", ".join(df.columns)}'
                print(f"ERROR: {mensaje_error}")
                return jsonify({
                    'success': False,
                    'message': mensaje_error
                })
            
            # Procesar datos
            errores_validacion = []
            registros_exitosos = 0
            registros_actualizados = 0
            
            cur = mysql.connection.cursor()
            usuario_actual = session.get('usuario')
            
            # Obtener ID del usuario
            cur.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario_actual,))
            usuario_data = cur.fetchone()
            usuario_id = usuario_data['id'] if usuario_data else None
            
            print(f"Procesando {len(df)} filas...")
            
            for index, row in df.iterrows():
                try:
                    # Validar campos obligatorios
                    if pd.isna(row['id_camaras']) or str(row['id_camaras']).strip() == '':
                        errores_validacion.append(f"Fila {index + 2}: ID de cámara es obligatorio")
                        continue
                    
                    if pd.isna(row['correo']) or str(row['correo']).strip() == '':
                        errores_validacion.append(f"Fila {index + 2}: Correo es obligatorio")
                        continue
                    
                    if pd.isna(row['nombre']) or str(row['nombre']).strip() == '':
                        errores_validacion.append(f"Fila {index + 2}: Nombre es obligatorio")
                        continue
                    
                    # Preparar datos
                    id_camara = str(row['id_camaras']).strip()
                    correo = str(row['correo']).strip()
                    nombre = str(row['nombre']).strip()
                    estado = 1 if pd.isna(row.get('estado')) else (1 if str(row['estado']).lower() in ['1', 'true', 'activo', 'si'] else 0)
                    regional = str(row.get('regional', '')).strip() if not pd.isna(row.get('regional')) else ''
                    
                    # Procesar coordenadas
                    latitud = None
                    longitud = None
                    if not pd.isna(row.get('latitud')):
                        try:
                            latitud = float(row['latitud'])
                        except (ValueError, TypeError):
                            print(f"Advertencia: Latitud inválida en fila {index + 2}: {row.get('latitud')}")
                    
                    if not pd.isna(row.get('longitud')):
                        try:
                            longitud = float(row['longitud'])
                        except (ValueError, TypeError):
                            print(f"Advertencia: Longitud inválida en fila {index + 2}: {row.get('longitud')}")
                    
                    print(f"Procesando {id_camara}: lat={latitud}, lng={longitud}")
                    
                    # Verificar si existe
                    cur.execute("SELECT id_camaras FROM camaras WHERE id_camaras = %s", (id_camara,))
                    existe = cur.fetchone()
                    
                    if existe:
                        # Actualizar
                        cur.execute("""
                            UPDATE camaras SET correo = %s, nombre = %s, estado = %s, regional = %s, 
                                             latitud = %s, longitud = %s
                            WHERE id_camaras = %s
                        """, (correo, nombre, estado, regional, latitud, longitud, id_camara))
                        registros_actualizados += 1
                        print(f"Actualizada: {id_camara}")
                    else:
                        # Insertar
                        cur.execute("""
                            INSERT INTO camaras (id_camaras, correo, nombre, estado, regional, 
                                               latitud, longitud, fecha_creacion, usuario_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (id_camara, correo, nombre, estado, regional, latitud, longitud, datetime.date.today(), usuario_id))
                        registros_exitosos += 1
                        print(f"Creada: {id_camara}")
                
                except Exception as e:
                    error_msg = f"Fila {index + 2}: {str(e)}"
                    errores_validacion.append(error_msg)
                    print(f"ERROR: {error_msg}")
            
            # Confirmar cambios
            mysql.connection.commit()
            cur.close()
            
            # Respuesta
            total_procesados = registros_exitosos + registros_actualizados
            mensaje = f"Procesamiento completado. {registros_exitosos} creadas, {registros_actualizados} actualizadas."
            
            if errores_validacion:
                mensaje += f" {len(errores_validacion)} errores."
            
            print(f"=== RESULTADO ===")
            print(f"Exitosos: {registros_exitosos}, Actualizados: {registros_actualizados}")
            print(f"Errores: {len(errores_validacion)}")
            
            return jsonify({
                'success': True,
                'message': mensaje,
                'detalles': {
                    'registros_exitosos': registros_exitosos,
                    'registros_actualizados': registros_actualizados,
                    'total_procesados': total_procesados,
                    'errores': errores_validacion[:5]  # Solo primeros 5 errores
                }
            })
            
        except Exception as e:
            print(f"ERROR GENERAL: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en la importación: {str(e)}'
            })

    @staticmethod
    def exportar_camaras():
        """
        Exporta todas las cámaras a un archivo Excel
        """
        try:
            cur = mysql.connection.cursor()
            
            # Obtener todas las cámaras
            cur.execute("""
                SELECT id_camaras, correo, nombre, estado, regional, 
                       latitud, longitud, fecha_creacion
                FROM camaras 
                ORDER BY fecha_creacion DESC
            """)
            
            camaras = cur.fetchall()
            cur.close()
            
            if not camaras:
                return jsonify({
                    'success': False,
                    'message': 'No hay cámaras para exportar'
                })
            
            # Convertir a DataFrame
            df = pd.DataFrame(camaras)
            
            # Renombrar columnas
            df.columns = ['ID Cámara', 'Correo', 'Nombre', 'Estado', 'Regional', 'Latitud', 'Longitud', 'Fecha Creación']
            
            # Convertir estado
            df['Estado'] = df['Estado'].apply(lambda x: 'Activo' if x == 1 else 'Inactivo')
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"camaras_export_{timestamp}.xlsx"
                
                df.to_excel(tmp.name, sheet_name='Cámaras', index=False, engine='openpyxl')
                tmp_path = tmp.name
            
            return send_file(
                tmp_path,
                as_attachment=True,
                download_name=nombre_archivo,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error exportando cámaras: {str(e)}'
            })
