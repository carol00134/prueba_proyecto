-- =====================================================
-- SCRIPT PARA AGREGAR COLUMNAS LATITUD Y LONGITUD
-- =====================================================
-- Descripción: Agrega las columnas latitud y longitud a las tablas
-- tickets y camaras para manejar coordenadas geográficas
-- Fecha: 2025-10-06
-- =====================================================

USE proyecto;

-- Agregar columnas latitud y longitud a la tabla tickets
ALTER TABLE tickets 
ADD COLUMN latitud DECIMAL(10,8) NULL COMMENT 'Latitud de la ubicación (-90 a 90)',
ADD COLUMN longitud DECIMAL(11,8) NULL COMMENT 'Longitud de la ubicación (-180 a 180)';

-- Agregar columnas latitud y longitud a la tabla camaras
ALTER TABLE camaras 
ADD COLUMN latitud DECIMAL(10,8) NULL COMMENT 'Latitud de la ubicación de la cámara (-90 a 90)',
ADD COLUMN longitud DECIMAL(11,8) NULL COMMENT 'Longitud de la ubicación de la cámara (-180 a 180)';

-- Crear índices para las consultas geográficas (opcional pero recomendado)
CREATE INDEX idx_tickets_lat_lng ON tickets(latitud, longitud);
CREATE INDEX idx_camaras_lat_lng ON camaras(latitud, longitud);

-- Verificar que las columnas se agregaron correctamente
DESCRIBE tickets;
DESCRIBE camaras;

-- =====================================================
-- NOTAS SOBRE LAS COLUMNAS
-- =====================================================
-- DECIMAL(10,8) para latitud: permite 2 dígitos antes del punto decimal y 8 después
-- Esto da una precisión de aproximadamente 1 metro
-- 
-- DECIMAL(11,8) para longitud: permite 3 dígitos antes del punto decimal y 8 después
-- Esto cubre el rango completo de longitudes (-180 a 180) con alta precisión
--
-- Las columnas son NULL para mantener compatibilidad con datos existentes
-- =====================================================

SHOW COLUMNS FROM tickets LIKE '%latitud%';
SHOW COLUMNS FROM tickets LIKE '%longitud%';
SHOW COLUMNS FROM camaras LIKE '%latitud%';
SHOW COLUMNS FROM camaras LIKE '%longitud%';
