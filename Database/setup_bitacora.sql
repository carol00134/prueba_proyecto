-- Script para agregar la tabla de bitácora a la base de datos existente

USE proyecto;

-- Crear tabla de bitácora
CREATE TABLE IF NOT EXISTS bitacora (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    usuario_nombre VARCHAR(100) NOT NULL,
    accion VARCHAR(255) NOT NULL,
    modulo VARCHAR(100) NOT NULL,
    descripcion TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    datos_anteriores JSON,
    datos_nuevos JSON,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índices para mejorar rendimiento
    INDEX idx_usuario_id (usuario_id),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_modulo (modulo),
    INDEX idx_accion (accion),
    
    -- Clave foránea con usuarios
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comentario de la tabla
ALTER TABLE bitacora COMMENT = 'Registro de todas las actividades realizadas por usuarios del sistema';

-- Insertar algunos registros de ejemplo para pruebas
INSERT INTO bitacora (usuario_id, usuario_nombre, accion, modulo, descripcion, ip_address) 
SELECT 
    1, 
    'admin', 
    'SYSTEM_SETUP', 
    'Sistema', 
    'Configuración inicial del módulo de bitácora',
    '127.0.0.1'
WHERE EXISTS (SELECT 1 FROM usuarios WHERE id = 1);

SELECT 'Tabla de bitácora creada exitosamente' as Resultado;