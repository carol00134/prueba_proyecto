-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
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
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (rol_id) REFERENCES roles(id)
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
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
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
    FOREIGN KEY (tipologia_id) REFERENCES tipologias(id)
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL, -- quien crea la ficha
    fecha DATETIME NOT NULL,
    departamento_id INT NOT NULL,
    municipio_id INT NOT NULL,
    coordenada VARCHAR(50),
    tipologia_id INT NOT NULL,
    subtipologia_id INT,
    descripcion TEXT,
    nota_respaldo TEXT,
    registro TEXT,
    mando TEXT,
    nota_final TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
    FOREIGN KEY (municipio_id) REFERENCES municipios(id),
    FOREIGN KEY (tipologia_id) REFERENCES tipologias(id),
    FOREIGN KEY (subtipologia_id) REFERENCES subtipologias(id)
);

-- Relación ficha <-> despachos (varios despachos por ficha)
CREATE TABLE ticket_despacho (
    ticket_id INT NOT NULL,
    despacho_id INT NOT NULL,
    PRIMARY KEY (ticket_id, despacho_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (despacho_id) REFERENCES despachos(id)
);

-- Relación ficha <-> unidades (varias unidades por ficha)
CREATE TABLE ticket_unidad (
    ticket_id INT NOT NULL,
    unidad_id INT NOT NULL,
    PRIMARY KEY (ticket_id, unidad_id),
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (unidad_id) REFERENCES unidades(id)
);
