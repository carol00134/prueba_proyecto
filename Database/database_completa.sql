-- =====================================================
-- SCRIPT COMPLETO DE BASE DE DATOS - PROYECTO FLASK
-- =====================================================
-- Autor: Sistema de Gestión
-- Fecha: 2025-09-23
-- Descripción: Script completo para crear la base de datos
-- con toda la estructura y datos iniciales
-- =====================================================

-- Crear base de datos (opcional - descomenta si necesitas crearla)
-- CREATE DATABASE IF NOT EXISTS proyecto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE proyecto;

-- Eliminar tablas existentes (en orden correcto por dependencias)
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS acceso_modulo;
DROP TABLE IF EXISTS ticket_unidad;
DROP TABLE IF EXISTS ticket_despacho;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS usuario_rol;
DROP TABLE IF EXISTS puntos_geograficos;
DROP TABLE IF EXISTS camaras;
DROP TABLE IF EXISTS subtipologias;
DROP TABLE IF EXISTS municipios;
DROP TABLE IF EXISTS tipologias;
DROP TABLE IF EXISTS departamentos;
DROP TABLE IF EXISTS unidades;
DROP TABLE IF EXISTS despachos;
DROP TABLE IF EXISTS modulos;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- ESTRUCTURA DE TABLAS
-- =====================================================

-- Tabla de roles
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de usuarios (ACTUALIZADA con campo regional obligatorio)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    regional VARCHAR(100) NOT NULL COMMENT 'Regional o zona geográfica del usuario (campo obligatorio)',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relación usuario-rol (muchos a muchos)
CREATE TABLE usuario_rol (
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    PRIMARY KEY (usuario_id, rol_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de departamentos
CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de municipios
CREATE TABLE municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    departamento_id INT NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de tipologías
CREATE TABLE tipologias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de subtipologías
CREATE TABLE subtipologias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipologia_id INT NOT NULL,
    FOREIGN KEY (tipologia_id) REFERENCES tipologias(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de instituciones despachadas
CREATE TABLE despachos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de unidades movilizadas
CREATE TABLE unidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Módulos del sistema
CREATE TABLE modulos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla principal de tickets/fichas
CREATE TABLE tickets (
    id VARCHAR(50) PRIMARY KEY,
    usuario_id INT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    regional VARCHAR(50),
    departamento_id INT,
    municipio_id INT,
    location POINT NOT NULL,
    tipologia_id INT,
    subtipologia_id INT,
    descripcion TEXT,
    nota_respaldo TEXT,
    registro TEXT,
    mando TEXT,
    nota_final TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id) ON DELETE SET NULL,
    FOREIGN KEY (tipologia_id) REFERENCES tipologias(id) ON DELETE SET NULL,
    FOREIGN KEY (subtipologia_id) REFERENCES subtipologias(id) ON DELETE SET NULL,
    SPATIAL INDEX(location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relación ficha <-> despachos (varios despachos por ficha)
CREATE TABLE ticket_despacho (
    ticket_id VARCHAR(50) NOT NULL,
    despacho_id INT NOT NULL,
    PRIMARY KEY (ticket_id, despacho_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (despacho_id) REFERENCES despachos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Relación ficha <-> unidades (varias unidades por ficha)
CREATE TABLE ticket_unidad (
    ticket_id VARCHAR(50) NOT NULL,
    unidad_id INT NOT NULL,
    PRIMARY KEY (ticket_id, unidad_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (unidad_id) REFERENCES unidades(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permisos de acceso: qué rol puede acceder a qué módulo
CREATE TABLE acceso_modulo (
    rol_id INT NOT NULL,
    modulo_id INT NOT NULL,
    PRIMARY KEY (rol_id, modulo_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de puntos geográficos
CREATE TABLE puntos_geograficos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    departamento_id INT,
    municipio_id INT,
    direccion VARCHAR(255),
    location POINT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    SPATIAL INDEX(location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de cámaras
CREATE TABLE camaras (
    id_camaras VARCHAR(50) PRIMARY KEY,
    correo VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    regional VARCHAR(50),
    fecha_creacion DATE,
    fecha_ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cambio_password BOOLEAN DEFAULT FALSE,
    usuario_id INT,
    rol_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar roles básicos
INSERT INTO roles (nombre) VALUES 
('administrador'),
('operador'),
('supervisor');

-- Insertar usuarios iniciales (con regional obligatorio)
INSERT INTO usuarios (usuario, contraseña, nombre, activo, regional) VALUES
('admin', 'facil', 'Administrador', TRUE, 'Central'),
('call', 'facil', 'Call Center', TRUE, 'Central'),
('master', 'facil', 'Master', TRUE, 'Central');

-- Asignar roles a usuarios
INSERT INTO usuario_rol (usuario_id, rol_id) VALUES
(1, 1), -- admin -> administrador
(2, 2), -- call -> operador
(3, 3); -- master -> supervisor

-- Insertar departamentos de Honduras
INSERT INTO departamentos (nombre) VALUES
('Atlántida'),
('Choluteca'),
('Colón'),
('Comayagua'),
('Copán'),
('Cortés'),
('El Paraíso'),
('Francisco Morazán'),
('Gracias a Dios'),
('Intibucá'),
('Islas de la Bahía'),
('La Paz'),
('Lempira'),
('Ocotepeque'),
('Olancho'),
('Santa Bárbara'),
('Valle'),
('Yoro');

-- Insertar municipios por departamento
-- ATLÁNTIDA
INSERT INTO municipios (nombre, departamento_id) VALUES
('La Ceiba', 1),
('El Porvenir', 1),
('Esparta', 1),
('Jutiapa', 1),
('La Masica', 1),
('San Francisco', 1),
('Tela', 1),
('Arizona', 1),

-- CHOLUTECA
('Choluteca', 2),
('Apacilagua', 2),
('Concepción de María', 2),
('Duyure', 2),
('El Corpus', 2),
('El Triunfo', 2),
('Marcovia', 2),
('Morolica', 2),
('Namasigüe', 2),
('Orocuina', 2),
('Pespire', 2),
('San Antonio de Flores', 2),
('San Isidro', 2),
('San José', 2),
('San Marcos de Colón', 2),

-- COLÓN
('Trujillo', 3),
('Balfate', 3),
('Iriona', 3),
('Limón', 3),
('Sabá', 3),
('Santa Fe', 3),
('Santa Rosa de Aguán', 3),
('Sonaguera', 3),
('Tocoa', 3),
('Bonito Oriental', 3),

-- COMAYAGUA
('Comayagua', 4),
('Ajuterique', 4),
('El Rosario', 4),
('Esquías', 4),
('Humuya', 4),
('La Libertad', 4),
('Lamaní', 4),
('La Trinidad', 4),
('Lejamaní', 4),
('Meámbar', 4),
('Minas de Oro', 4),
('Ojos de Agua', 4),
('San Jerónimo', 4),
('San José de Comayagua', 4),
('San José del Potrero', 4),
('San Luis', 4),
('San Sebastián', 4),
('Siguatepeque', 4),
('Villa de San Antonio', 4),
('Las Lajas', 4),
('Taulabé', 4),

-- COPÁN
('Santa Rosa de Copán', 5),
('Cabañas', 5),
('Concepción', 5),
('Copán Ruinas', 5),
('Corquín', 5),
('Cucuyagua', 5),
('Dolores', 5),
('Dulce Nombre', 5),
('El Paraíso', 5),
('Florida', 5),
('La Jigua', 5),
('La Unión', 5),
('Nueva Arcadia', 5),
('San Agustín', 5),
('San Antonio', 5),
('San Jerónimo', 5),
('San José', 5),
('San Juan de Opoa', 5),
('San Nicolás', 5),
('San Pedro', 5),
('Santa Rita', 5),
('Trinidad de Copán', 5),
('Veracruz', 5),

-- CORTÉS
('San Pedro Sula', 6),
('Choloma', 6),
('Omoa', 6),
('Pimienta', 6),
('Potrerillos', 6),
('Puerto Cortés', 6),
('San Antonio de Cortés', 6),
('San Francisco de Yojoa', 6),
('San Manuel', 6),
('Santa Cruz de Yojoa', 6),
('Villanueva', 6),
('La Lima', 6),

-- EL PARAÍSO
('Yuscarán', 7),
('Alauca', 7),
('Danlí', 7),
('El Paraíso', 7),
('Güinope', 7),
('Jacaleapa', 7),
('Liure', 7),
('Morocelí', 7),
('Oropolí', 7),
('Potrerillos', 7),
('San Antonio de Flores', 7),
('San Lucas', 7),
('San Matías', 7),
('Soledad', 7),
('Teupasenti', 7),
('Texiguat', 7),
('Vado Ancho', 7),
('Yauyupe', 7),
('Trojes', 7),

-- FRANCISCO MORAZÁN
('Tegucigalpa', 8),
('Alubarén', 8),
('Cedros', 8),
('Curarén', 8),
('El Porvenir', 8),
('Guaimaca', 8),
('La Libertad', 8),
('La Venta', 8),
('Lepaterique', 8),
('Maraita', 8),
('Marale', 8),
('Nueva Armenia', 8),
('Ojojona', 8),
('Orica', 8),
('Reitoca', 8),
('Sabanagrande', 8),
('San Antonio de Oriente', 8),
('San Buenaventura', 8),
('San Ignacio', 8),
('San Juan de Flores', 8),
('San Miguelito', 8),
('Santa Ana', 8),
('Santa Lucía', 8),
('Talanga', 8),
('Tatumbla', 8),
('Valle de Ángeles', 8),
('Villa de San Francisco', 8),
('Vallecillo', 8),

-- GRACIAS A DIOS
('Puerto Lempira', 9),
('Brus Laguna', 9),
('Ahuas', 9),
('Juan Francisco Bulnes', 9),
('Ramón Villeda Morales', 9),
('Wampusirpe', 9),

-- INTIBUCÁ
('La Esperanza', 10),
('Camasca', 10),
('Colomoncagua', 10),
('Concepción', 10),
('Dolores', 10),
('Intibucá', 10),
('Jesús de Otoro', 10),
('Magdalena', 10),
('Masaguara', 10),
('San Antonio', 10),
('San Isidro', 10),
('San Juan', 10),
('San Marcos de la Sierra', 10),
('San Miguelito', 10),
('Santa Lucía', 10),
('Yamaranguila', 10),
('San Francisco de Opalaca', 10),

-- ISLAS DE LA BAHÍA
('Utila', 11),
('Guanaja', 11),
('Roatán', 11),

-- LA PAZ
('La Paz', 12),
('Aguanqueterique', 12),
('Cabañas', 12),
('Cane', 12),
('Chinacla', 12),
('Guajiquiro', 12),
('Lauterique', 12),
('Marcala', 12),
('Mercedes de Oriente', 12),
('Opatoro', 12),
('San Antonio del Norte', 12),
('San José', 12),
('San Juan', 12),
('San Pedro de Tutule', 12),
('Santa Ana', 12),
('Santa Elena', 12),
('Santa María', 12),
('Santiago de Puringla', 12),
('Yarula', 12),

-- LEMPIRA
('Gracias', 13),
('Belén', 13),
('Candelaria', 13),
('Cololaca', 13),
('Erandique', 13),
('Gualcinse', 13),
('Guarita', 13),
('La Campa', 13),
('La Iguala', 13),
('Las Flores', 13),
('La Unión', 13),
('La Virtud', 13),
('Lepaera', 13),
('Mapulaca', 13),
('Piraera', 13),
('San Andrés', 13),
('San Francisco', 13),
('San Juan Guarita', 13),
('San Manuel Colohete', 13),
('San Marcos de Caiquín', 13),
('San Rafael', 13),
('San Sebastián', 13),
('Santa Cruz', 13),
('Talgua', 13),
('Tambla', 13),
('Tomalá', 13),
('Valladolid', 13),
('Virginia', 13),

-- OCOTEPEQUE
('Nueva Ocotepeque', 14),
('Belén Gualcho', 14),
('Concepción', 14),
('Dolores Merendón', 14),
('Fraternidad', 14),
('La Encarnación', 14),
('La Labor', 14),
('Lucerna', 14),
('Mercedes', 14),
('San Fernando', 14),
('San Francisco del Valle', 14),
('San Jorge', 14),
('San Marcos', 14),
('Santa Fe', 14),
('Sensenti', 14),
('Sinuapa', 14),

-- OLANCHO
('Juticalpa', 15),
('Campamento', 15),
('Catacamas', 15),
('Concordia', 15),
('Dulce Nombre de Culmí', 15),
('El Rosario', 15),
('Esquipulas del Norte', 15),
('Gualaco', 15),
('Guarizama', 15),
('Guata', 15),
('Guayape', 15),
('Jano', 15),
('La Unión', 15),
('Mangulile', 15),
('Manto', 15),
('Salamá', 15),
('San Esteban', 15),
('San Francisco de Becerra', 15),
('San Francisco de la Paz', 15),
('Santa María del Real', 15),
('Silca', 15),
('Yocón', 15),
('Patuca', 15),

-- SANTA BÁRBARA
('Santa Bárbara', 16),
('Arada', 16),
('Atima', 16),
('Azacualpa', 16),
('Ceguaca', 16),
('Concepción del Norte', 16),
('Concepción del Sur', 16),
('Chinda', 16),
('El Níspero', 16),
('Gualala', 16),
('Ilama', 16),
('Las Vegas', 16),
('Macuelizo', 16),
('Naranjito', 16),
('Nuevo Celilac', 16),
('Petoa', 16),
('Protección', 16),
('Quimistán', 16),
('San Francisco de Ojuera', 16),
('San José de Colinas', 16),
('San Luis', 16),
('San Marcos', 16),
('San Nicolás', 16),
('San Pedro Zacapa', 16),
('San Vicente Centenario', 16),
('Santa Rita', 16),
('Trinidad', 16),

-- VALLE
('Nacaome', 17),
('Alianza', 17),
('Amapala', 17),
('Aramecina', 17),
('Caridad', 17),
('Goascorán', 17),
('Langue', 17),
('San Francisco de Coray', 17),
('San Lorenzo', 17),

-- YORO
('Yoro', 18),
('Arenal', 18),
('El Negrito', 18),
('El Progreso', 18),
('Jocón', 18),
('Morazán', 18),
('Olanchito', 18),
('Santa Rita', 18),
('Sulaco', 18),
('Victoria', 18),
('Yorito', 18);

-- Insertar tipologías
INSERT INTO tipologias (id, nombre) VALUES
(1, 'COLISION VEHICULAR'),
(2, 'DELITOS CONTRA LA VIDA'),
(3, 'DELITOS CONTRA LA PROPIEDAD'),
(4, 'DELITOS CONTRA LA LIBERTAD'),
(5, 'DELITOS CONTRA LA FAMILIA'),
(6, 'DELITOS SEXUALES'),
(7, 'DELITOS CONTRA LA SEGURIDAD'),
(8, 'SALUD MENTAL'),
(9, 'EMERGENCIAS'),
(10, 'LESIONES'),
(11, 'VIOLENCIA DOMESTICA'),
(12, 'SEGURIDAD CIUDADANA'),
(13, 'MUERTE'),
(14, 'OTROS'),
(15, 'ELECTORAL'),
(16, 'DELITOS ELECTORALES'),
(17, 'ASISTENCIA SOCIAL');

-- Insertar subtipologías (selección de las más importantes)
INSERT INTO subtipologias (id, nombre, tipologia_id) VALUES
(1, 'Colisión Entre Vehículos', 1),
(2, 'Atropello', 1),
(3, 'Volcamiento', 1),
(4, 'Colisión Contra Objeto Fijo', 1),
(5, 'Homicidio', 2),
(6, 'Asesinato', 2),
(7, 'Parricidio', 2),
(8, 'Infanticidio', 2),
(9, 'Robo', 3),
(10, 'Hurto', 3),
(11, 'Robo de Vehículo', 3),
(12, 'Robo a Casa de Habitación', 3),
(13, 'Secuestro', 4),
(14, 'Extorsión', 4),
(15, 'Privación de Libertad', 4),
(16, 'Violación', 6),
(17, 'Estupro', 6),
(18, 'Acoso Sexual', 6),
(19, 'Intento de Suicidio', 8),
(20, 'Crisis Psicótica', 8),
(21, 'Depresión Severa', 8),
(22, 'Incendio', 9),
(23, 'Inundación', 9),
(24, 'Terremoto', 9),
(25, 'Lesiones Leves', 10),
(26, 'Lesiones Graves', 10),
(27, 'Violencia Intrafamiliar', 11),
(28, 'Maltrato Infantil', 11),
(29, 'Disturbios', 12),
(30, 'Riña', 12),
(31, 'Muerte Natural', 13),
(32, 'Muerte Violenta', 13),
(33, 'Persona Extraviada', 14),
(34, 'Accidente Laboral', 14),
(35, 'Manifestaciones Pacíficas', 15),
(36, 'Irregularidades Electorales', 15),
(37, 'Fraude Electoral', 16),
(38, 'Compra de Votos', 16),
(39, 'Atención Médica', 17),
(40, 'Atención Psicológica', 17);

-- Insertar despachos (instituciones)
INSERT INTO despachos (id, nombre) VALUES
(1, 'Policía Nacional'),
(2, 'UME'),
(3, 'Bomberos'),
(4, 'Cruz Roja'),
(5, 'URPA'),
(6, 'COPECO'),
(7, 'Policía Militar'),
(8, 'Psicología'),
(9, 'SIAT Transito'),
(10, 'DIPOL'),
(11, 'ATIC'),
(12, 'DIPANCO'),
(13, 'DPI'),
(14, 'DSTU'),
(15, 'Alcaldía'),
(16, 'SENAF'),
(17, 'UREM');

-- Insertar unidades
INSERT INTO unidades (id, nombre) VALUES
(1, 'Patrulla PN'),
(2, 'Ambulancia CR'),
(3, 'Motorizada PN'),
(4, 'Transito-T'),
(5, 'HRB Incendio'),
(6, 'HRB Apoyo'),
(7, 'Mensaje Enviado'),
(8, 'Moto ambulancia'),
(9, 'Asistencia psicologica'),
(10, 'PatrullaPM'),
(11, 'Ambulancia UME'),
(12, 'Motorizada PM'),
(13, 'Transito-movil'),
(14, 'HRB Rescate'),
(15, 'HRB Ambulancia'),
(16, 'Patrullaje a pie'),
(17, 'Ambulancia UREM');

-- =====================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para búsquedas frecuentes
CREATE INDEX idx_usuarios_regional ON usuarios(regional);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_tickets_fecha ON tickets(fecha_hora);
CREATE INDEX idx_tickets_regional ON tickets(regional);
CREATE INDEX idx_municipios_departamento ON municipios(departamento_id);
CREATE INDEX idx_subtipologias_tipologia ON subtipologias(tipologia_id);

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS ÚTILES
-- =====================================================

DELIMITER //

-- Procedimiento para obtener estadísticas de usuarios por regional
CREATE PROCEDURE GetUsuariosPorRegional()
BEGIN
    SELECT 
        regional,
        COUNT(*) as total_usuarios,
        SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as usuarios_activos,
        SUM(CASE WHEN activo = 0 THEN 1 ELSE 0 END) as usuarios_inactivos
    FROM usuarios 
    GROUP BY regional 
    ORDER BY total_usuarios DESC;
END //

-- Procedimiento para obtener municipios por departamento
CREATE PROCEDURE GetMunicipiosByDepartamento(IN dept_id INT)
BEGIN
    SELECT m.id, m.nombre, d.nombre as departamento
    FROM municipios m
    JOIN departamentos d ON m.departamento_id = d.id
    WHERE m.departamento_id = dept_id
    ORDER BY m.nombre;
END //

DELIMITER ;

-- =====================================================
-- CONFIGURACIONES FINALES
-- =====================================================

-- Configurar charset por defecto
ALTER DATABASE proyecto CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- Verificar integridad de datos
SELECT 'Base de datos creada exitosamente' as status;

-- Mostrar resumen de datos insertados
SELECT 
    (SELECT COUNT(*) FROM roles) as total_roles,
    (SELECT COUNT(*) FROM usuarios) as total_usuarios,
    (SELECT COUNT(*) FROM departamentos) as total_departamentos,
    (SELECT COUNT(*) FROM municipios) as total_municipios,
    (SELECT COUNT(*) FROM tipologias) as total_tipologias,
    (SELECT COUNT(*) FROM subtipologias) as total_subtipologias,
    (SELECT COUNT(*) FROM despachos) as total_despachos,
    (SELECT COUNT(*) FROM unidades) as total_unidades;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
-- Script generado el: 2025-09-23
-- Última modificación: Campo regional obligatorio agregado
-- Total de tablas: 14
-- =====================================================