#!/usr/bin/env python3
"""
Script para probar directamente el endpoint de cámaras
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.mapas_controller import MapasController
import json

def test_camaras_endpoint():
    """Prueba directamente el método get_camaras()"""
    
    print("🔍 Probando endpoint de cámaras para el mapa...")
    
    try:
        # Llamar directamente al método
        controller = MapasController()
        response = controller.get_camaras()
        
        # Obtener los datos JSON
        if hasattr(response, 'get_json'):
            data = response.get_json()
        else:
            data = response.json if hasattr(response, 'json') else response
        
        print(f"📊 Respuesta del endpoint:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data and 'features' in data:
            features = data['features']
            print(f"\n📍 Total de cámaras encontradas: {len(features)}")
            
            if len(features) > 0:
                print("\n📹 Detalles de las cámaras:")
                for i, feature in enumerate(features, 1):
                    props = feature['properties']
                    coords = feature['geometry']['coordinates']
                    print(f"  {i}. {props['nombre']} (ID: {props['id']})")
                    print(f"     Coordenadas: [{coords[0]}, {coords[1]}]")
                    print(f"     Regional: {props['regional']}")
            else:
                print("❌ No se encontraron cámaras en el endpoint")
        else:
            print("❌ Respuesta inválida del endpoint")
            
        return data
        
    except Exception as e:
        print(f"❌ Error al probar endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_camaras_endpoint()