-- GreenCore Seed Data
-- Generado automaticamente desde modelo.json
-- Idempotente: ON CONFLICT DO NOTHING / WHERE NOT EXISTS

-- ZONAS
INSERT INTO zonas (nombre, descripcion, capacidad_maxima, temperatura_minima, temperatura_maxima, humedad_minima, humedad_maxima, activa, creado_en) VALUES ('Zona A - Tropicales', 'Zona dedicada a plantas tropicales de alta humedad', 200, 18.0, 30.0, 60.0, 85.0, TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO zonas (nombre, descripcion, capacidad_maxima, temperatura_minima, temperatura_maxima, humedad_minima, humedad_maxima, activa, creado_en) VALUES ('Zona B - Suculentas', 'Zona de baja humedad para cactus y suculentas', 150, 20.0, 35.0, 30.0, 55.0, TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;
INSERT INTO zonas (nombre, descripcion, capacidad_maxima, temperatura_minima, temperatura_maxima, humedad_minima, humedad_maxima, activa, creado_en) VALUES ('Zona C - Aromaticas', 'Zona de plantas aromaticas y medicinales', 100, 15.0, 25.0, 50.0, 70.0, TRUE, NOW()) ON CONFLICT (nombre) DO NOTHING;

-- CLIENTES
INSERT INTO clientes (nombre, email, telefono, ciudad, activo, creado_en) VALUES ('Vivero El Rosal', 'compras@elrosal.com', '+57 310 555 1234', 'Neiva', TRUE, NOW()) ON CONFLICT (email) DO NOTHING;
INSERT INTO clientes (nombre, email, telefono, ciudad, activo, creado_en) VALUES ('Flores del Valle', 'contacto@floresdelvalle.com', '+57 314 222 5678', 'Bogota', TRUE, NOW()) ON CONFLICT (email) DO NOTHING;
INSERT INTO clientes (nombre, email, telefono, ciudad, activo, creado_en) VALUES ('Jardines Verdes', 'ventas@jardinesverdes.com', '+57 300 888 9012', 'Medellin', TRUE, NOW()) ON CONFLICT (email) DO NOTHING;

-- SENSORES
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-TEMP-001', 'TEMPERATURA', 24.5, 'C', 18.0, 30.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona A - Tropicales'), NOW()) ON CONFLICT (codigo) DO NOTHING;
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-HUM-001', 'HUMEDAD', 72.3, '%', 60.0, 85.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona A - Tropicales'), NOW()) ON CONFLICT (codigo) DO NOTHING;
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-TEMP-002', 'TEMPERATURA', 28.1, 'C', 20.0, 35.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona B - Suculentas'), NOW()) ON CONFLICT (codigo) DO NOTHING;
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-HUM-002', 'HUMEDAD', 42.0, '%', 30.0, 55.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona B - Suculentas'), NOW()) ON CONFLICT (codigo) DO NOTHING;
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-TEMP-003', 'TEMPERATURA', 21.0, 'C', 15.0, 25.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona C - Aromaticas'), NOW()) ON CONFLICT (codigo) DO NOTHING;
INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, estado, ultima_lectura, zona_id, creado_en) VALUES ('SNS-LUZ-001', 'LUMINOSIDAD', 3200.0, 'lux', 1000.0, 5000.0, 'ACTIVO', NOW(), (SELECT id FROM zonas WHERE nombre = 'Zona C - Aromaticas'), NOW()) ON CONFLICT (codigo) DO NOTHING;

-- PLANTAS
INSERT INTO plantas (nombre, especie, lote, cantidad, precio, estado, fecha_siembra, fecha_estimada_venta, descripcion, imagen_url, zona_id, creado_en) VALUES ('Orquidea Phalaenopsis', 'Phalaenopsis amabilis', 'LOT-2026-001', 50, 35000.00, 'CRECIMIENTO', '2026-01-15', '2026-06-01', 'Variedad de alta demanda, requiere riego cada 3 dias', NULL, (SELECT id FROM zonas WHERE nombre = 'Zona A - Tropicales'), NOW()) ON CONFLICT (lote) DO NOTHING;
INSERT INTO plantas (nombre, especie, lote, cantidad, precio, estado, fecha_siembra, fecha_estimada_venta, descripcion, imagen_url, zona_id, creado_en) VALUES ('Bromelia Imperial', 'Aechmea fasciata', 'LOT-2026-002', 30, 28000.00, 'LISTA_VENTA', '2025-10-01', '2026-02-01', 'Lista para comercializar, alta rotacion', NULL, (SELECT id FROM zonas WHERE nombre = 'Zona A - Tropicales'), NOW()) ON CONFLICT (lote) DO NOTHING;
INSERT INTO plantas (nombre, especie, lote, cantidad, precio, estado, fecha_siembra, fecha_estimada_venta, descripcion, imagen_url, zona_id, creado_en) VALUES ('Cactus Saguaro', 'Carnegiea gigantea', 'LOT-2026-003', 100, 15000.00, 'GERMINANDO', '2026-03-01', '2026-12-01', 'Cactus de crecimiento lento, bajo mantenimiento', NULL, (SELECT id FROM zonas WHERE nombre = 'Zona B - Suculentas'), NOW()) ON CONFLICT (lote) DO NOTHING;
INSERT INTO plantas (nombre, especie, lote, cantidad, precio, estado, fecha_siembra, fecha_estimada_venta, descripcion, imagen_url, zona_id, creado_en) VALUES ('Lavanda Vera', 'Lavandula angustifolia', 'LOT-2026-004', 80, 12000.00, 'CRECIMIENTO', '2026-02-01', '2026-07-01', 'Aromatica de alta demanda en mercado local', NULL, (SELECT id FROM zonas WHERE nombre = 'Zona C - Aromaticas'), NOW()) ON CONFLICT (lote) DO NOTHING;

-- LECTURAS SENSOR (solo si la tabla esta vacia)
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 24.5, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-001' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 25.1, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-001' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 72.3, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-HUM-001' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 28.1, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-002' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 42.0, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-HUM-002' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 31.2, TRUE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-001' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 21.0, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-003' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);
INSERT INTO lecturas_sensor (valor, fuera_de_rango, "timestamp", sensor_id) SELECT 3200.0, FALSE, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-LUZ-001' AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);

-- ALERTAS (solo si la tabla esta vacia)
INSERT INTO alertas (mensaje, nivel, leida, correo_enviado, valor_registrado, "timestamp", sensor_id) SELECT 'Temperatura en Zona A supero el umbral maximo (31.2 > 30.0)', 'CRITICO', FALSE, TRUE, 31.2, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-TEMP-001' AND NOT EXISTS (SELECT 1 FROM alertas);
INSERT INTO alertas (mensaje, nivel, leida, correo_enviado, valor_registrado, "timestamp", sensor_id) SELECT 'Humedad en Zona B por debajo del umbral minimo (27.0 < 30.0)', 'ADVERTENCIA', FALSE, FALSE, 27.0, NOW(), s.id FROM sensores s WHERE s.codigo = 'SNS-HUM-002' AND NOT EXISTS (SELECT 1 FROM alertas);
