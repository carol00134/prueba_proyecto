-- Insertar algunos departamentos de ejemplo si no existen
INSERT IGNORE INTO departamentos (id, nombre) VALUES
(1, 'Antioquia'),
(2, 'Cundinamarca'), 
(3, 'Valle del Cauca'),
(4, 'Atlántico'),
(5, 'Santander');

-- Insertar algunos municipios de ejemplo
INSERT IGNORE INTO municipios (id, nombre, departamento_id) VALUES
(1, 'Medellín', 1),
(2, 'Envigado', 1),
(3, 'Bello', 1),
(4, 'Itagüí', 1),
(5, 'Bogotá', 2),
(6, 'Soacha', 2),
(7, 'Chía', 2),
(8, 'Cali', 3),
(9, 'Palmira', 3),
(10, 'Buenaventura', 3),
(11, 'Barranquilla', 4),
(12, 'Soledad', 4),
(13, 'Bucaramanga', 5),
(14, 'Floridablanca', 5);