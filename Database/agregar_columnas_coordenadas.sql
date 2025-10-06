-- Script para agregar columnas de coordenadas a la tabla camaras
-- Ejecutar este script para agregar las columnas latitud y longitud

USE tu_base_de_datos; -- Cambia esto por el nombre de tu base de datos

-- Agregar columnas de latitud y longitud a la tabla camaras
ALTER TABLE camaras 
ADD COLUMN latitud DECIMAL(10,8) NULL COMMENT 'Latitud de la ubicación de la cámara',
ADD COLUMN longitud DECIMAL(11,8) NULL COMMENT 'Longitud de la ubicación de la cámara';

-- Verificar que las columnas se agregaron correctamente
DESCRIBE camaras;