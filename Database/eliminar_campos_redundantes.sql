-- EJECUTAR ESTE SCRIPT PARA ELIMINAR CAMPOS REDUNDANTES
-- ¡IMPORTANTE! Hacer backup antes de ejecutar

-- Paso 1: Verificar que el campo POINT tiene datos válidos
SELECT COUNT(*) as tickets_con_coordenadas
FROM tickets 
WHERE location IS NOT NULL 
  AND ST_X(location) != 0 
  AND ST_Y(location) != 0;

-- Paso 2: Ver una muestra de los datos que se van a conservar
SELECT id, 
       ST_Y(location) as latitud_final, 
       ST_X(location) as longitud_final
FROM tickets 
WHERE location IS NOT NULL 
ORDER BY id LIMIT 5;

-- Paso 3: ELIMINAR LAS COLUMNAS REDUNDANTES
ALTER TABLE tickets DROP COLUMN latitud;
ALTER TABLE tickets DROP COLUMN longitud;

-- Paso 4: Verificar estructura final
DESCRIBE tickets;

-- Paso 5: Confirmar que los datos siguen estando disponibles
SELECT id, 
       ST_Y(location) as latitud, 
       ST_X(location) as longitud
FROM tickets 
WHERE location IS NOT NULL 
ORDER BY id LIMIT 3;