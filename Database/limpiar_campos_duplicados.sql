-- Script para eliminar campos duplicados latitud/longitud
-- RECOMENDACIÓN: Usar solo el campo location POINT

-- PASO 1: Verificar que todos los tickets tengan coordenadas válidas en POINT
SELECT 
    id,
    latitud as lat_campo_separado,
    longitud as lng_campo_separado,
    ST_Y(location) as lat_from_point,
    ST_X(location) as lng_from_point,
    CASE 
        WHEN ST_Y(location) BETWEEN -4 AND 15 AND ST_X(location) BETWEEN -82 AND -66 THEN 'Válidas'
        WHEN ST_Y(location) = 0 AND ST_X(location) = 0 THEN 'Sin coordenadas'
        ELSE 'Revisar'
    END as estado
FROM tickets 
ORDER BY id;

-- PASO 2: HACER BACKUP antes de eliminar columnas
-- mysqldump -u root proyecto tickets > backup_tickets.sql

-- PASO 3: Eliminar las columnas redundantes (EJECUTAR SOLO SI ESTÁS SEGURO)
-- ALTER TABLE tickets DROP COLUMN latitud;
-- ALTER TABLE tickets DROP COLUMN longitud;

-- PASO 4: Verificar estructura final
-- DESCRIBE tickets;