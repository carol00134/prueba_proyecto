-- Script para agregar coordenadas a la tabla de cámaras
-- Ejecutar este script en tu base de datos

USE proyecto;

-- Agregar campos de latitud y longitud a la tabla camaras
ALTER TABLE camaras 
ADD COLUMN latitud DECIMAL(10, 8) NULL COMMENT 'Latitud de la ubicación de la cámara',
ADD COLUMN longitud DECIMAL(11, 8) NULL COMMENT 'Longitud de la ubicación de la cámara';

-- Crear índice para mejorar búsquedas por ubicación
CREATE INDEX idx_camaras_coordinates ON camaras(latitud, longitud);

-- Opcional: Agregar algunos datos de ejemplo con coordenadas
-- (puedes comentar esta sección si ya tienes datos)
/*
UPDATE camaras SET latitud = 14.0723, longitud = -87.1921 WHERE id_camaras = 'CAM001'; -- Centro Tegucigalpa
UPDATE camaras SET latitud = 15.5041, longitud = -88.0250 WHERE id_camaras = 'CAM002'; -- San Pedro Sula
UPDATE camaras SET latitud = 15.7597, longitud = -86.7822 WHERE id_camaras = 'CAM003'; -- La Ceiba
UPDATE camaras SET latitud = 14.0839, longitud = -87.1712 WHERE id_camaras = 'CAM004'; -- Universidad
UPDATE camaras SET latitud = 14.0608, longitud = -87.2172 WHERE id_camaras = 'CAM005'; -- Aeropuerto
*/

COMMIT;