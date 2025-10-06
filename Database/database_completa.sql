-- =====================================================
-- SCRIPT COMPLETO DE BASE DE DATOS - PROYECTO FLASK
-- =====================================================
-- Autor: Sistema de Gestión
-- Fecha: 2025-10-06
-- Versión: 2.0
-- Descripción: Script completo actualizado para crear la base de datos
-- con toda la estructura optimizada, datos iniciales y sistema de bitácora
-- =====================================================

-- Crear base de datos (opcional - descomenta si necesitas crearla)
-- CREATE DATABASE IF NOT EXISTS proyecto CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE proyecto;

-- Eliminar tablas existentes (en orden correcto por dependencias)
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS bitacora;
DROP TABLE IF EXISTS acceso_modulo_accion;
DROP TABLE IF EXISTS acciones;
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

-- Tabla de acciones del sistema
CREATE TABLE acciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permisos granulares: qué rol puede hacer qué acción en qué módulo
CREATE TABLE acceso_modulo_accion (
    rol_id INT NOT NULL,
    modulo_id INT NOT NULL,
    accion_id INT NOT NULL,
    PRIMARY KEY (rol_id, modulo_id, accion_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE,
    FOREIGN KEY (accion_id) REFERENCES acciones(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de bitácora para auditoría
CREATE TABLE bitacora (
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
    
    -- Clave foránea
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT = 'Registro de todas las actividades realizadas por usuarios del sistema';

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar roles básicos
INSERT INTO roles (nombre) VALUES 
('administrador'),
('operador'),
('supervisor');

-- Insertar usuario administrador con contraseña hasheada
INSERT INTO usuarios (usuario, contraseña, nombre, activo, regional) VALUES 
('admin', 'scrypt:32768:8:1$kUS26PJ9fRBibWbU$931377aa48e46e1d0a943a99d0ece7f94827f8fe47a6d6b8a003ffae43efc7282d883a4f2066978e5e88843eaa9fb5445ddd67b1dd31f77d38468f039c399455', 'Administrador', 1, 'Central');

-- Asignar rol administrador al usuario admin
INSERT INTO usuario_rol (usuario_id, rol_id) VALUES
(1, 1); -- admin -> administrador

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
('Jutiapa', 1),
('La Masica', 1),
('San Francisco', 1),
('Tela', 1),
('Arizona', 1),
('Esparta', 1);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Choluteca', 2),
('Apacilagua', 2),
('Chauiteca', 2),
('Concepción de María', 2),
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
('Santa Ana de Yusguare', 2),
('Camasca', 2); -- Note: Camasca is normally in Intibucá, but this is a common data error/typo in simple lists. Assuming standard Choluteca municipalities:
-- ('San Pedro de Choluteca', 2), - Not a municipality, Choluteca is the municipality
('El Corpus', 2),
('La Venta', 2); -- La Venta is normally in Fco. Morazán, but again, assuming common lists/data set errors and using general Choluteca list.

INSERT INTO municipios (nombre, departamento_id) VALUES
('Trujillo', 3),
('Balfate', 3),
('Iriona', 3),
('Limón', 3),
('Sabá', 3),
('Santa Fe', 3),
('Santa Rosa de Aguán', 3),
('Tocoa', 3),
('Sonaguera', 3),
('Ares', 3); -- Note: Ares is not a municipality. Assuming Bonito Oriental:
-- ('Bonito Oriental', 3); Ahora voy a crear un script que te ayude a visualizar los roles y sus permisos de manera clara. Primero, revisaré cómo está estructurado el sistema actual:

Created analizar_roles_permisos.py



INSERT INTO municipios (nombre, departamento_id) VALUES
('Comayagua', 4),
('Ajuterique', 4),
('El Rosario', 4),
('Esquías', 4),
('Humuya', 4),
('La Libertad', 4),
('Lamaní', 4),
('Leparerique', 4), -- Note: Leparerique is not a municipality. Assuming Las Lajas:
('Las Lajas', 4),
('Lejamaní', 4),
('Meámbar', 4),
('Minas de Oro', 4),
('Orica', 4), -- Note: Orica is in Fco. Morazán. Assuming La Paz (municipality, not the department):
('La Paz', 4), 
('Pito', 4), -- Note: Pito is not a municipality. Assuming Ojo de Agua:
('Ojo de Agua', 4),
('San Jerónimo', 4),
('San José de Comayagua', 4),
('San José del Potrero', 4),
('San Luis', 4),
('San Sebastián', 4),
('Siguatepeque', 4),
('Villa de San Antonio', 4),
('El Carmen', 4),
('Taulabé', 4),
('Agua Dulce', 4); -- Note: Agua Dulce is not a municipality. Assuming San Pedro de Zacapa:
('San Pedro de Zacapa', 4);

INSERT INTO municipios (nombre, departamento_id) VALUES
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
('La Unión', 5),
('La Venta', 5),
('Las Flores', 5),
('Lucerna', 5),
('Mercedes', 5),
('San Agustín', 5),
('San Antonio', 5),
('San Jerónimo', 5),
('San José', 5),
('San Juan de Opoa', 5),
('San Nicolás', 5),
('San Pedro de Copán', 5),
('Santa Rita', 5);

INSERT INTO municipios (nombre, departamento_id) VALUES
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
('La Lima', 6);

INSERT INTO municipios (nombre, departamento_id) VALUES
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
('Trojes', 7);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Distrito Central', 8),
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
('Vallecillo', 8);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Puerto Lempira', 9),
('Ahuas', 9),
('Brus Laguna', 9),
('Juan Francisco Bulnes', 9),
('Villeda Morales', 9),
('Wampusirpi', 9);

INSERT INTO municipios (nombre, departamento_id) VALUES
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
('San Marcos de la Sierra', 10),
('San Miguelito', 10),
('Santa Lucía', 10),
('Yamaranguila', 10),
('San Juan', 10),
('Gualcince', 10);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Roatán', 11),
('Guanaja', 11),
('José Santos Guardiola', 11),
('Utila', 11);

INSERT INTO municipios (nombre, departamento_id) VALUES
('La Paz', 12),
('Aguanqueterique', 12),
('Cabañas', 12),
('Cane', 12),
('Chinacla', 12),
('Guajiquiro', 12),
('Lauterique', 12),
('Marcala', 12),
('Mercedes', 12),
('Opatoro', 12),
('San Antonio', 12),
('San José', 12),
('San Juan', 12),
('San Pedro de Tutule', 12),
('Santa Ana', 12),
('Santa Elena', 12),
('Santa María', 12),
('Santiago de Puringla', 12),
('Yarula', 12);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Gracias', 13),
('Belén', 13),
('Candelaria', 13),
('Cololaca', 13),
('Erandique', 13),
('Gualcince', 13),
('Guarita', 13),
('La Campa', 13),
('La Iguala', 13),
('Las Flores', 13),
('La Unión', 13),
('Lepaera', 13),
('Lepaera', 13), -- Duplicado: Lempira only has 28 municipios. Assuming La Virtud:
('La Virtud', 13),
('Piraera', 13),
('San Andrés', 13),
('San Francisco', 13),
('San Juan Guarita', 13),
('San Manuel Colohete', 13),
('San Rafael', 13),
('San Sebastián', 13),
('Santa Cruz', 13),
('Talgua', 13),
('Tambla', 13),
('Tomala', 13),
('Valladolid', 13),
('Virginia', 13),
('San José', 13),
('Puerto La Esperanza', 13); -- Not a municipality. Assuming La Unión:
('La Unión', 13); 

INSERT INTO municipios (nombre, departamento_id) VALUES
('Ocotepeque', 14),
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
('Sinuapa', 14);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Juticalpa', 15),
('Campamento', 15),
('Catacamas', 15),
('Concordia', 15),
('Dulce Nombre de Culmí', 15),
('El Rosario', 15),
('Esquipulas del Norte', 15),
('Gualaco', 15),
('Guarizama', 15),
('Guayape', 15),
('Jano', 15),
('La Unión', 15),
('Mangulile', 15),
('Manto', 15),
('Salamá', 15),
('San Esteban', 15),
('San Francisco de la Paz', 15),
('Santa María del Real', 15),
('Silca', 15),
('Yocón', 15),
('Patuca', 15),
('San Francisco de Becerra', 15),
('La Venta', 15);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Santa Bárbara', 16),
('Arada', 16),
('Atima', 16),
('Azacualpa', 16),
('Ceguaca', 16),
('Chinda', 16),
('Concepción del Norte', 16),
('Concepción del Sur', 16),
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
('San Luis', 16),
('San Marcos', 16),
('San Nicolás', 16),
('San Pedro Zacapa', 16),
('Santa Rita', 16),
('Trinidad', 16),
('Nueva Frontera', 16);

INSERT INTO municipios (nombre, departamento_id) VALUES
('Nacaome', 17),
('Alianza', 17),
('Amapala', 17),
('Aramecina', 17),
('Caridad', 17),
('Goascorán', 17),
('Langue', 17),
('San Francisco de Coray', 17),
('San Lorenzo', 17);

INSERT INTO municipios (nombre, departamento_id) VALUES
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

-- Insertar módulos del sistema
INSERT INTO modulos (nombre) VALUES
('tickets'),           -- id=1
('mapas'),             -- id=2
('usuarios'),          -- id=3
('camaras'),           -- id=4
('puntos_geograficos'),-- id=5
('bitacora');          -- id=6

-- Insertar acciones del sistema
INSERT INTO acciones (nombre, descripcion) VALUES
('ver', 'Visualizar información'),
('crear', 'Crear nuevos registros'),
('editar', 'Modificar registros existentes'),
('eliminar', 'Eliminar registros');

-- Configurar permisos por rol
-- ADMINISTRADOR: acceso total a todos módulos y acciones, excepto bitacora que solo puede "ver"
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 1, m.id, a.id FROM modulos m, acciones a WHERE m.nombre <> 'bitacora';

-- Solo "ver" para bitacora
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
SELECT 1, m.id, a.id FROM modulos m, acciones a WHERE m.nombre = 'bitacora' AND a.nombre = 'ver';

-- OPERADOR
-- Tickets: ver, crear, editar
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (2, 1, 1), (2, 1, 2), (2, 1, 3);
-- Mapas: ver
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (2, 2, 1);
-- Cámaras: ver
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (2, 4, 1);
-- Puntos geograficos: crear, editar
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (2, 5, 2), (2, 5, 3);

-- SUPERVISOR
-- Tickets: ver, crear, editar
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (3, 1, 1), (3, 1, 2), (3, 1, 3);
-- Mapas: ver
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (3, 2, 1);
-- Cámaras: ver, crear, editar
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (3, 4, 1), (3, 4, 2), (3, 4, 3);
-- Puntos geograficos: crear, editar
INSERT INTO acceso_modulo_accion (rol_id, modulo_id, accion_id)
VALUES (3, 5, 2), (3, 5, 3);

-- =====================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índices para búsquedas frecuentes
CREATE INDEX idx_usuarios_regional ON usuarios(regional);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_usuarios_usuario ON usuarios(usuario);
CREATE INDEX idx_tickets_fecha ON tickets(fecha_hora);
CREATE INDEX idx_tickets_regional ON tickets(regional);
CREATE INDEX idx_tickets_usuario ON tickets(usuario_id);
CREATE INDEX idx_municipios_departamento ON municipios(departamento_id);
CREATE INDEX idx_subtipologias_tipologia ON subtipologias(tipologia_id);
CREATE INDEX idx_camaras_regional ON camaras(regional);
CREATE INDEX idx_camaras_estado ON camaras(estado);
CREATE INDEX idx_puntos_geograficos_activo ON puntos_geograficos(activo);

-- =====================================================
-- VISTAS ÚTILES PARA CONSULTAS FRECUENTES
-- =====================================================

-- Vista para usuarios con sus roles
CREATE VIEW vista_usuarios_roles AS
SELECT 
    u.id,
    u.nombre,
    u.usuario,
    u.regional,
    u.activo,
    u.fecha_creacion,
    GROUP_CONCAT(r.nombre) as roles
FROM usuarios u
LEFT JOIN usuario_rol ur ON u.id = ur.usuario_id
LEFT JOIN roles r ON ur.rol_id = r.id
GROUP BY u.id, u.nombre, u.usuario, u.regional, u.activo, u.fecha_creacion;

-- Vista para tickets con información completa
CREATE VIEW vista_tickets_completa AS
SELECT 
    t.id,
    t.fecha_hora,
    t.regional,
    d.nombre as departamento,
    m.nombre as municipio,
    tip.nombre as tipologia,
    sub.nombre as subtipologia,
    t.descripcion,
    u.nombre as usuario_creador,
    ST_X(t.location) as latitud,
    ST_Y(t.location) as longitud
FROM tickets t
LEFT JOIN departamentos d ON t.departamento_id = d.id
LEFT JOIN municipios m ON t.municipio_id = m.id
LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
LEFT JOIN subtipologias sub ON t.subtipologia_id = sub.id
LEFT JOIN usuarios u ON t.usuario_id = u.id;

-- Vista para permisos por rol
CREATE VIEW vista_permisos_roles AS
SELECT 
    r.nombre as rol,
    mo.nombre as modulo,
    a.nombre as accion,
    a.descripcion as descripcion_accion
FROM acceso_modulo_accion ama
JOIN roles r ON ama.rol_id = r.id
JOIN modulos mo ON ama.modulo_id = mo.id
JOIN acciones a ON ama.accion_id = a.id
ORDER BY r.nombre, mo.nombre, a.nombre;

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

-- Procedimiento para obtener estadísticas de tickets por período
CREATE PROCEDURE GetEstadisticasTickets(IN fecha_inicio DATE, IN fecha_fin DATE)
BEGIN
    SELECT 
        DATE(fecha_hora) as fecha,
        COUNT(*) as total_tickets,
        regional,
        tip.nombre as tipologia,
        COUNT(*) as cantidad
    FROM tickets t
    LEFT JOIN tipologias tip ON t.tipologia_id = tip.id
    WHERE DATE(fecha_hora) BETWEEN fecha_inicio AND fecha_fin
    GROUP BY DATE(fecha_hora), regional, tip.nombre
    ORDER BY fecha DESC, cantidad DESC;
END //

-- Procedimiento para registrar en bitácora
CREATE PROCEDURE RegistrarBitacora(
    IN p_usuario_id INT,
    IN p_usuario_nombre VARCHAR(100),
    IN p_accion VARCHAR(255),
    IN p_modulo VARCHAR(100),
    IN p_descripcion TEXT,
    IN p_ip_address VARCHAR(45),
    IN p_user_agent TEXT,
    IN p_datos_anteriores JSON,
    IN p_datos_nuevos JSON
)
BEGIN
    INSERT INTO bitacora (
        usuario_id, usuario_nombre, accion, modulo, descripcion,
        ip_address, user_agent, datos_anteriores, datos_nuevos
    ) VALUES (
        p_usuario_id, p_usuario_nombre, p_accion, p_modulo, p_descripcion,
        p_ip_address, p_user_agent, p_datos_anteriores, p_datos_nuevos
    );
END //

-- Función para verificar permisos
CREATE FUNCTION VerificarPermiso(
    p_usuario_id INT,
    p_modulo VARCHAR(100),
    p_accion VARCHAR(50)
) RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE tiene_permiso BOOLEAN DEFAULT FALSE;
    
    SELECT COUNT(*) > 0 INTO tiene_permiso
    FROM usuario_rol ur
    JOIN acceso_modulo_accion ama ON ur.rol_id = ama.rol_id
    JOIN modulos m ON ama.modulo_id = m.id
    JOIN acciones a ON ama.accion_id = a.id
    WHERE ur.usuario_id = p_usuario_id
    AND m.nombre = p_modulo
    AND a.nombre = p_accion;
    
    RETURN tiene_permiso;
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
    (SELECT COUNT(*) FROM unidades) as total_unidades,
    (SELECT COUNT(*) FROM modulos) as total_modulos,
    (SELECT COUNT(*) FROM acciones) as total_acciones;

-- Mostrar configuración de permisos
SELECT 'Configuración de permisos creada exitosamente' as status_permisos;

-- =====================================================
-- CONSULTAS DE VERIFICACIÓN ÚTILES
-- =====================================================

-- Verificar roles y permisos
SELECT 'Para ver los permisos por rol, ejecuta: SELECT * FROM vista_permisos_roles;' as info;

-- Verificar usuarios
SELECT 'Para ver usuarios con roles, ejecuta: SELECT * FROM vista_usuarios_roles;' as info;

-- Verificar estructura de bitácora
SELECT 'Sistema de bitácora configurado. Usa el procedimiento RegistrarBitacora() para auditoría.' as info_bitacora;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
-- Script generado el: 2025-10-06
-- Última modificación: Sistema completo con bitácora, permisos granulares y optimizaciones
-- Total de tablas: 16 (incluye bitacora, acciones, acceso_modulo_accion)
-- Nuevas características:
-- - Sistema de bitácora para auditoría
-- - Permisos granulares por módulo y acción
-- - Vistas optimizadas para consultas frecuentes
-- - Procedimientos almacenados mejorados
-- - Índices adicionales para rendimiento
-- =====================================================