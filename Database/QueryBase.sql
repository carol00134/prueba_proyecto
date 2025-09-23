-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de roles
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Relación usuario-rol (muchos a muchos)
CREATE TABLE usuario_rol (
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    PRIMARY KEY (usuario_id, rol_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Catálogo de departamentos
CREATE TABLE departamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Catálogo de municipios
CREATE TABLE municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    departamento_id INT NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE CASCADE
);

-- Catálogo de tipologías
CREATE TABLE tipologias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Catálogo de subtipologías
CREATE TABLE subtipologias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipologia_id INT NOT NULL,
    FOREIGN KEY (tipologia_id) REFERENCES tipologias(id) ON DELETE CASCADE
);

-- Catálogo de instituciones despachadas
CREATE TABLE despachos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Catálogo de unidades movilizadas
CREATE TABLE unidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla principal de tickets/fichas
CREATE TABLE tickets (
    id VARCHAR(50) PRIMARY KEY,
    usuario_id INT, -- permite NULL
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
);

ALTER TABLE tickets AUTO_INCREMENT = 1;

-- Relación ficha <-> despachos (varios despachos por ficha)
CREATE TABLE ticket_despacho (
    ticket_id VARCHAR(50) NOT NULL,
    despacho_id INT NOT NULL,
    PRIMARY KEY (ticket_id, despacho_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (despacho_id) REFERENCES despachos(id) ON DELETE CASCADE
);

-- Relación ficha <-> unidades (varias unidades por ficha)
CREATE TABLE ticket_unidad (
    ticket_id VARCHAR(50) NOT NULL,
    unidad_id INT NOT NULL,
    PRIMARY KEY (ticket_id, unidad_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (unidad_id) REFERENCES unidades(id) ON DELETE CASCADE
);

-- Módulos del sistema
CREATE TABLE modulos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- Permisos de acceso: qué rol puede acceder a qué módulo
CREATE TABLE acceso_modulo (
    rol_id INT NOT NULL,
    modulo_id INT NOT NULL,
    PRIMARY KEY (rol_id, modulo_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (modulo_id) REFERENCES modulos(id) ON DELETE CASCADE
);

INSERT INTO roles (nombre) VALUES 
  ('administrador'),
  ('operador'),
  ('supervisor');

  INSERT INTO usuarios (usuario, contraseña, nombre, activo) VALUES
  ('admin', 'facil', 'Administrador', TRUE),
  ('call',  'facil', 'Call Center', TRUE),
  ('master', 'facil', 'Master', TRUE);

  INSERT INTO usuario_rol (usuario_id, rol_id) VALUES
  (1, 1), -- admin -> administrador
  (2, 2), -- call -> call center
  (3, 3); -- master -> master

  CREATE TABLE puntos_geograficos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    departamento_id INT,                  -- Relación con tabla departamentos
    municipio_id INT,                     -- Relación con tabla municipios
    direccion VARCHAR(255),
    location POINT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT,                       -- Relación con tabla usuarios
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (municipio_id) REFERENCES municipios(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    SPATIAL INDEX(location)
);

TRUNCATE TABLE departamentos;

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

INSERT INTO municipios (nombre, departamento_id) VALUES
('La Ceiba', 1),
('El Porvenir', 1),
('Esparta', 1),
('Jutiapa', 1),
('La Masica', 1),
('San Francisco', 1),
('Tela', 1),
('Arizona', 1),

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

('San Pedro Sula', 6),
('Choloma', 6),
('La Lima', 6),
('Pimienta', 6),
('Potrerillos', 6),
('Puerto Cortés', 6),
('San Antonio de Cortés', 6),
('San Francisco de Yojoa', 6),
('San Manuel', 6),
('Santa Cruz de Yojoa', 6),
('Villanueva', 6),
('Omoa', 6),

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
('Vallecillo', 8),

('Puerto Lempira', 9),
('Brus Laguna', 9),
('Ahuas', 9),
('Juan Francisco Bulnes', 9),
('Ramón Villeda Morales', 9),
('Wampusirpe', 9),

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

('Utila', 11),
('Guanaja', 11),
('Roatán', 11),

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
('San José de las Colinas', 16),
('San Luis', 16),
('San Marcos', 16),
('San Nicolás', 16),
('San Pedro Zacapa', 16),
('San Vicente Centenario', 16),
('Santa Rita', 16),
('Trinidad', 16),
('Las Vegas', 16),

('Nacaome', 17),
('Alianza', 17),
('Amapala', 17),
('Aramecina', 17),
('Caridad', 17),
('Goascorán', 17),
('Langue', 17),
('San Francisco de Coray', 17),
('San Lorenzo', 17),

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

TRUNCATE TABLE tipologias;
ALTER TABLE tipologias AUTO_INCREMENT = 1;

INSERT INTO tipologias (nombre) VALUES
('Accidente de Transito'),
('Asistencia'),
('Casos de alcadia'),
('Delitos Comunes'),
('Delitos Contra la Mujer U hombre'),
('Delitos Contra la niñez Adolescencia'),
('Delitos Contra la Propiedad'),
('Delitos Contra la Vida'),
('Desastres Naturales'),
('Emergencia Medica'),
('Incendio'),
('Investigacion'),
('Otras Causas de Muerte'),
('Reportes Recibidos');

-- Catálogo de Tipos de Incidentes (tipologías)
CREATE TABLE tipos_incidentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_incidente VARCHAR(150) NOT NULL,
    estado TINYINT NOT NULL DEFAULT 1
);

-- Catálogo de Subtipos de Incidentes (subtipologías)
CREATE TABLE subtipos_incidentes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subtipo_incidente VARCHAR(150) NOT NULL,
    tipos_incidentes_id INT NOT NULL,
    estado TINYINT NOT NULL DEFAULT 1,
    FOREIGN KEY (tipos_incidentes_id) REFERENCES tipos_incidentes(id) ON DELETE CASCADE
);

-- Emergencias Médicas (catálogo aparte)
CREATE TABLE emergencias_medicas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emergencia_medica VARCHAR(150) NOT NULL
);

TRUNCATE TABLE subtipologias;
ALTER TABLE subtipologias AUTO_INCREMENT = 1;

INSERT INTO subtipologias (id, nombre, tipologia_id) VALUES
(6, 'Volcamiento', 1),
(7, 'Asistencia', 2),
(8, 'Asistencia Psicológica', 2),
(9, 'Ayuda Humanitaria', 2),
(10, 'Covid-19', 2),
(11, 'Eventos Públicos', 2),
(12, 'Resguardo Policial / Presencia Policial', 2),
(13, 'Alteración De Linderos', 3),
(14, 'Conflicto Vecinal', 3),
(15, 'Congestionamiento', 3),
(16, 'Desalojo O Readecuacion/Cierre De Establecimiento', 3),
(17, 'Invasión De Vía Pública', 3),
(18, 'Ley Seca', 3),
(19, 'Mendicidad', 3),
(20, 'Negocios Clandestinos', 3),
(21, 'Problemas De Agua Potable', 3),
(22, 'Quema De Basura', 3),
(23, 'Semáforo En Mal Estado', 3),
(24, 'Semovientes', 3),
(25, 'Tala De Árboles', 3),
(26, 'Vehículo Abandonado', 3),
(27, 'Vehículo En Mal Estado', 3),
(28, 'Vehículos Mal Estacionados', 3),
(29, 'Venta De Pólvora', 3),
(30, 'Allanamiento De Domicilio', 4),
(31, 'Amenazas', 4),
(32, 'Chantaje', 4),
(33, 'Conducción Temeraria', 4),
(34, 'Contrabando', 4),
(35, 'Delitos Ambientales', 4),
(36, 'Delitos De Desobediencia', 4),
(37, 'Delitos Contra Derechos Laborales', 4),
(38, 'Desórdenes Públicos', 4),
(39, 'Estragos', 4),
(40, 'Exhibicionismo', 4),
(41, 'Injurias Y Calumnias', 4),
(42, 'Maltrato O Abandono Animal', 4),
(43, 'Perturbación Del Orden', 4),
(44, 'Quebrantamiento De Condena O Medida', 4),
(45, 'Abandono Ancianos/Personas Con Discapacidad/Personas Enfermas', 5),
(46, 'Bigamia', 5),
(47, 'Delitos Contra La Libertad Religiosa / Práctica De Rituales', 5),
(48, 'Discriminación', 5),
(49, 'Hostigamiento Sexual', 5),
(50, 'Maltrato Familiar', 5),
(51, 'Otras Agresiones Sexuales', 5),
(52, 'Tentativa De Violación', 5),
(53, 'Trata De Personas', 5),
(54, 'Trato Degradante', 5),
(55, 'Violación Sexual', 5),
(56, 'Violencia Doméstica', 5),
(57, 'Abandono De Menores', 6),
(58, 'Estupro', 6),
(59, 'Explotación Laboral Infantil', 6),
(60, 'Hostigamiento Sexual', 6),
(61, 'Incesto', 6),
(62, 'Incumplimiento Del Deber De Asistencia Y El Sustento', 6),
(63, 'Inducción Al Abandono Del Hogar', 6),
(64, 'Maltrato Familiar', 6),
(65, 'Otras Agresiones Sexuales', 6),
(66, 'Pornografía Infantil', 6),
(67, 'Sustracción De Menores', 6),
(68, 'Tentativa De Violación (Menores)', 6),
(69, 'Trata De Personas (Menores)', 6),
(70, 'Trato Degradante (Menores)', 6),
(71, 'Violación Sexual Especial', 6),
(72, 'Agiotaje', 7),
(73, 'Daños', 7),
(74, 'Estafa', 7),
(75, 'Extorsión', 7),
(76, 'Fraude', 7),
(77, 'Hurto A Comercio', 7),
(78, 'Hurto De Cosecha', 7),
(79, 'Hurto A Personas', 7),
(80, 'Hurto A Vehículo Automotor', 7),
(81, 'Hurto De Arma De Fuego', 7),
(82, 'Hurto De Vehículo', 7),
(83, 'Hurto A Vivienda', 7),
(84, 'Hurto De Ganado', 7),
(85, 'Hurto', 7),
(86, 'Loterías Y Juegos No Autorizados', 7),
(87, 'Robo De Arma De Fuego', 7),
(88, 'Robo A Comercio', 7),
(89, 'Robo A Personas', 7),
(90, 'Robo A Vehículo Automotor', 7),
(91, 'Robo A Vivienda', 7),
(92, 'Robo De Ganado', 7),
(93, 'Robo De Vehículo Automotor', 7),
(94, 'Robo', 7),
(95, 'Tentativa De Hurto', 7),
(96, 'Tentativa De Robo', 7),
(97, 'Usura', 7),
(98, 'Usurpación', 7),
(99, 'Aborto', 8),
(100, 'Amenazas A Muerte', 8),
(101, 'Atentado', 8),
(102, 'Femicidio', 8),
(103, 'Inducción Y Auxilio Al Suicidio', 8),
(104, 'Hallazgo De Feto/Bebé Humano', 8),
(105, 'Homicidio', 8),
(106, 'Tentativa De Homicidio', 8),
(107, 'Lesiones', 8),
(108, 'Parricidio', 8),
(109, 'Secuestro', 8),
(110, 'Privación Ilegal De La Libertad', 8),
(111, 'Asociación Terrorista', 8),
(112, 'Tortura', 8),
(113, 'Derrumbes', 9),
(114, 'Desbordamientos', 9),
(115, 'Deslave', 9),
(116, 'Fenómeno De Sequía', 9),
(117, 'Inundaciones', 9),
(118, 'Marejadas', 9),
(119, 'Maremoto', 9),
(120, 'Terremoto', 9),
(121, 'Tromba Marina', 9),
(122, 'Tsunami', 9),
(123, 'Vientos Racheados', 9),
(124, 'Emergencia Médica', 10),
(125, 'Covid-19', 10),
(126, 'Asesoria y Consulta Medica', 10),
(127, 'Líneas Y Tendido Eléctrico', 11),
(128, 'Embarcaciones', 11),
(129, 'Estructural', 11),
(130, 'Forestal', 11),
(131, 'Vehicular', 11),
(132, 'Zacatera', 11),
(133, 'Abuso De Autoridad/Violación De Deberes', 12),
(134, 'Activación De Alarmas', 12),
(135, 'Amotinamiento', 12),
(136, 'Asociación Ilícita', 12),
(137, 'Búsqueda', 12),
(138, 'Cohecho', 12),
(139, 'Consumo De Droga', 12),
(140, 'Desplazamiento Forzado', 12),
(141, 'Disparos Por Arma De Fuego', 12),
(142, 'Enfrentamiento Entre Grupos Delictivos', 12),
(143, 'Falsificación De Documentos', 12),
(144, 'Uso Indebido De Indumentaria Policial O Militar', 12),
(145, 'Decomisos', 12),
(146, 'Infracciones', 12),
(147, 'Personas Desaparecidas', 12),
(148, 'Persona Tendida En La Calle', 12),
(149, 'Personas Detenidas Por Causas Desconocidas', 12),
(150, 'Personas Sospechosas', 12),
(151, 'Reten/Operativo', 12),
(152, 'Requerimiento De Vehículo O Persona', 12),
(153, 'Saturaciones', 12),
(154, 'Seguimiento', 12),
(155, 'Tenencia Y Porte Ilegal De Armas', 12),
(156, 'Tráfico De Armas', 12),
(157, 'Tráfico De Drogas', 12),
(158, 'Tráfico Ilícito De Personas', 12),
(159, 'Traslado De Personas Detenidas', 12),
(160, 'Vehículos Sospechosos', 12),
(161, 'Venta De Droga', 12),
(162, 'Venta Y Consumo De Droga', 12),
(163, 'Muerte En Incendio', 13),
(164, 'Muerte Por Causas Naturales', 13),
(165, 'Muerte Por Sumersión', 13),
(166, 'Muerte Por Intoxicación', 13),
(167, 'Suicidio', 13),
(168, 'Muerte Por Atragantamiento', 13),
(169, 'Muerte Por Causas Desconocidas', 13),
(170, 'Muerte Por Aplastamiento Por Objeto Pesado', 13),
(171, 'Muerte Por Caída', 13),
(172, 'Muerte Por Electrocución', 13),
(173, 'Animales Muertos', 14),
(174, 'Animales Peligrosos', 14),
(175, 'Extravío De Chapa De Una Autoridad', 14),
(176, 'Extravío De Documentos Y Objetos Personales', 14),
(177, 'Extravío De Arma De Fuego', 14),
(178, 'Extravío De Placas Vehiculares', 14),
(179, 'Fuga De Sustancias Peligrosas E Inflamables', 14),
(180, 'Fumigación', 14),
(181, 'Manifestaciones Pacíficas', 14),
(182, 'Persona Extraviada', 14),
(183, 'Problemas En El Tendido Eléctrico', 14),
(184, 'Naufragio', 14),
(185, 'Quema De Pólvora', 14),
(186, 'Reporte Oficial De Día / Paramédico De Turno', 14),
(187, 'Refuerzo Policial', 14),
(188, 'Rescate Animal', 14),
(189, 'Respuesta A Denuncia', 14),
(190, 'Rescate A Personas', 14),
(191, 'Abuso de Autoridad', 15),
(192, 'Aglomeracion De Personas', 15),
(193, 'Cambio Injustificado Del Lugar De Votacion', 15),
(194, 'Coaccion Y Amenazas Electorales', 15),
(195, 'Comprar O Vender Votos', 15),
(196, 'Daños', 15),
(197, 'Destruccion de Propaganda', 15),
(198, 'Emergencia Medica', 15),
(199, 'Estructura Criminal Cerca De Los Centros De Votacion', 15),
(200, 'Extraccion De Votos Antes De La Verificacion Del Escrutinio', 15),
(201, 'Falsificacion De Documentos Electorales', 15),
(202, 'Impedir Revision De Urnas', 15),
(203, 'Incendios', 15),
(204, 'Irregularidad En Las Mesas Electorales', 15),
(205, 'Perturbacion Del Orden', 15),
(206, 'Retencion Material Electoral', 15),
(207, 'Ventas De Bebidas Alcohólicas', 15),
(208, 'Intento de suicidio', 8),
(209, 'Reportes DNI', 15),
(210, 'Seguimiento Medico', 10),
(211, 'Retencion ilicita de cedula', 16),
(212, 'Compra y venta de votos', 16),
(213, 'Alteracion del orden en el proceso electoral', 16),
(214, 'Abuso de autoridad electoral', 16),
(215, 'Intimidacion, engaño y acoso electoral', 16),
(216, 'Hurto o sabotaje al proceso electoral y de escrutinio', 16),
(217, 'Fraude electoral', 16),
(218, 'Destruccion de Propaganda', 16),
(219, 'Violacion del Secreto de Voto', 16),
(220, 'Campaña Electoral Ilegal', 16),
(221, 'Atencion Medica', 17),
(222, 'Atencion Psicologica', 17),
(223, 'Asesoria Legal', 17),
(224, 'Ayuda Humanitaria', 17);

SELECT * FROM tipologias;

-- INSERT para la tabla despachos según la imagen proporcionada

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

-- INSERT para la tabla unidades según la imagen proporcionada

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


CREATE TABLE camaras (
    id_camaras VARCHAR(50) PRIMARY KEY,
    correo VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    regional VARCHAR(50),
    fecha_creacion DATE,
    usuario_id INT,
    rol_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL
);
ALTER TABLE camaras
ADD FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL

TRUNCATE TABLE roles;
ALTER TABLE roles AUTO_INCREMENT = 1;