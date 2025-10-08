-- Script para configurar usuarios de prueba con roles
-- Ejecutar después de tener las tablas roles, usuarios y usuario_rol creadas

-- Insertar datos de prueba si no existen
-- Verificar que existan los roles
INSERT IGNORE INTO roles (id, nombre, descripcion) VALUES 
(1, 'administrador', 'Administrador del sistema con acceso completo'),
(2, 'operador', 'Operador con acceso a tickets, cámaras y mapas'),
(3, 'supervisor', 'Supervisor con acceso a cámaras, puntos geográficos y usuarios');

-- Crear usuarios de prueba (cambiar las contraseñas por hash reales)
INSERT IGNORE INTO usuarios (nombre, usuario, contraseña, regional, activo) VALUES 
('Administrador Prueba', 'admin_test', 'pbkdf2:sha256:600000$test$hashed_password', 'Regional Centro', 1),
('Operador Prueba', 'operador_test', 'pbkdf2:sha256:600000$test$hashed_password', 'Regional Norte', 1),
('Supervisor Prueba', 'supervisor_test', 'pbkdf2:sha256:600000$test$hashed_password', 'Regional Sur', 1);

-- Asignar roles a usuarios de prueba
-- Administrador
INSERT IGNORE INTO usuario_rol (usuario_id, rol_id) 
SELECT u.id, 1 FROM usuarios u WHERE u.usuario = 'admin_test';

-- Operador
INSERT IGNORE INTO usuario_rol (usuario_id, rol_id) 
SELECT u.id, 2 FROM usuarios u WHERE u.usuario = 'operador_test';

-- Supervisor
INSERT IGNORE INTO usuario_rol (usuario_id, rol_id) 
SELECT u.id, 3 FROM usuarios u WHERE u.usuario = 'supervisor_test';

-- Verificar que se hayan insertado correctamente
SELECT 
    u.nombre,
    u.usuario,
    GROUP_CONCAT(r.nombre) as roles
FROM usuarios u
LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
LEFT JOIN roles r ON ur.rol_id = r.id
WHERE u.usuario IN ('admin_test', 'operador_test', 'supervisor_test')
GROUP BY u.id;