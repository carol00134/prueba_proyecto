-- Script para corregir permisos según especificaciones exactas
-- Ejecutar después de tener las tablas creadas

-- Limpiar permisos existentes para reconfiguar correctamente
DELETE FROM acceso_modulo_accion;

-- ====== ADMINISTRADOR (ID: 1) ======
-- Acceso completo a todos los módulos y todas las acciones
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 1, m.id, a.id 
FROM modulos m 
CROSS JOIN acciones a;

-- ====== OPERADOR (ID: 2) ======
-- Tickets: crear, editar (solo los suyos), ver (solo los suyos)
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 2, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'tickets' AND a.nombre IN ('ver', 'crear', 'editar');

-- Cámaras: crear, ver (solo las suyas)
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 2, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'camaras' AND a.nombre IN ('ver', 'crear');

-- Mapas: solo ver
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 2, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'mapas' AND a.nombre = 'ver';

-- ====== SUPERVISOR (ID: 3) ======
-- Usuarios: solo ver (no puede crear usuarios)
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 3, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'usuarios' AND a.nombre = 'ver';

-- Cámaras: crear, editar, ver (no puede eliminar)
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 3, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'camaras' AND a.nombre IN ('ver', 'crear', 'editar');

-- Puntos geográficos: crear, editar, ver (no puede eliminar)
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 3, m.id, a.id 
FROM modulos m, acciones a 
WHERE m.nombre = 'puntos_geograficos' AND a.nombre IN ('ver', 'crear', 'editar');

-- Verificar permisos configurados
SELECT 
    r.nombre as rol,
    m.nombre as modulo,
    a.nombre as accion
FROM acceso_modulo_accion ama
JOIN roles r ON ama.rol_id = r.id
JOIN modulos m ON ama.modulo_id = m.id
JOIN acciones a ON ama.accion_id = a.id
ORDER BY r.id, m.id, a.id;