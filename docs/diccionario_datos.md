# Diccionario de Datos — GreenCore

**Sistema:** GreenCore — Gestión integral de invernadero  
**Base de datos:** PostgreSQL  
**Versión:** 1.0.0  
**Fecha:** 2026-05-23  

---

## Índice de Tablas

1. [zonas](#1-zonas)
2. [usuarios](#2-usuarios)
3. [plantas](#3-plantas)
4. [sensores](#4-sensores)
5. [lecturas_sensor](#5-lecturas_sensor)
6. [alertas](#6-alertas)
7. [clientes](#7-clientes)
8. [ventas](#8-ventas)

---

## Enumeraciones

| Enumeración | Valores posibles |
|---|---|
| `rol_usuario` | `ADMIN`, `OPERARIO`, `VISUALIZADOR` |
| `estado_planta` | `SEMILLA`, `GERMINANDO`, `CRECIMIENTO`, `LISTA_VENTA`, `VENDIDA`, `BAJA` |
| `tipo_sensor` | `TEMPERATURA`, `HUMEDAD`, `LUMINOSIDAD`, `CO2`, `PH_SUELO` |
| `estado_sensor` | `ACTIVO`, `INACTIVO`, `FALLA`, `CALIBRANDO` |
| `nivel_alerta` | `INFO`, `ADVERTENCIA`, `CRITICO` |
| `estado_venta` | `PENDIENTE`, `COMPLETADA`, `ANULADA` |

---

## 1. zonas

**Descripción:** Zona física del invernadero con condiciones controladas de temperatura y humedad.  
**Tabla BD:** `zonas`  
**Clase Java:** `com.greencore.model.Zona`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único de la zona |
| `nombre` | `nombre` | `String` | `VARCHAR(100)` | No | Sí | — | min=2, max=100 | Nombre descriptivo de la zona |
| `descripcion` | `descripcion` | `String` | `TEXT` | Sí | No | — | max=500 | Descripción detallada del propósito de la zona |
| `capacidadMaxima` | `capacidad_maxima` | `Integer` | `INTEGER` | No | No | — | min=1, max=10000 | Número máximo de plantas que puede albergar |
| `temperaturaMinima` | `temperatura_minima` | `Double` | `DOUBLE PRECISION` | No | No | — | min=-10.0, max=50.0 | Temperatura mínima permitida en °C |
| `temperaturaMaxima` | `temperatura_maxima` | `Double` | `DOUBLE PRECISION` | No | No | — | min=-10.0, max=50.0 | Temperatura máxima permitida en °C |
| `humedadMinima` | `humedad_minima` | `Double` | `DOUBLE PRECISION` | No | No | — | min=0.0, max=100.0 | Humedad relativa mínima en % |
| `humedadMaxima` | `humedad_maxima` | `Double` | `DOUBLE PRECISION` | No | No | — | min=0.0, max=100.0 | Humedad relativa máxima en % |
| `activa` | `activa` | `Boolean` | `BOOLEAN` | No | No | `true` | — | Indica si la zona está operativa |
| `creadoEn` | `creado_en` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de creación del registro |

**Relaciones:**
- `zonas` 1 → N `plantas` (a través de `zona_id` en `plantas`)
- `zonas` 1 → N `sensores` (a través de `zona_id` en `sensores`)

---

## 2. usuarios

**Descripción:** Usuario del sistema autenticado vía OAuth2 Google/Gmail. Creado automáticamente al primer inicio de sesión.  
**Tabla BD:** `usuarios`  
**Clase Java:** `com.greencore.model.Usuario`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único del usuario |
| `email` | `email` | `String` | `VARCHAR(255)` | No | Sí | — | formato email | Correo electrónico Gmail del usuario |
| `nombre` | `nombre` | `String` | `VARCHAR(150)` | No | No | — | min=2, max=150 | Nombre completo obtenido de Google |
| `fotoPerfil` | `foto_perfil` | `String` | `TEXT` | Sí | No | — | URL válida | URL de la foto de perfil de Google |
| `rol` | `rol` | `Enum(Role)` | `VARCHAR(30)` | No | No | `OPERARIO` | valores enum | Rol del usuario en el sistema |
| `provider` | `provider` | `String` | `VARCHAR(30)` | No | No | `GOOGLE` | — | Proveedor de autenticación OAuth2 |
| `providerId` | `provider_id` | `String` | `VARCHAR(255)` | No | Sí | — | Subject de Google | ID único del usuario en el proveedor OAuth2 |
| `activo` | `activo` | `Boolean` | `BOOLEAN` | No | No | `true` | — | Indica si el usuario puede acceder al sistema |
| `ultimoAcceso` | `ultimo_acceso` | `LocalDateTime` | `TIMESTAMP` | Sí | No | — | Actualizado en login | Fecha y hora del último inicio de sesión |
| `creadoEn` | `creado_en` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de creación del registro |

**Roles disponibles:**
| Rol | Descripción |
|---|---|
| `ADMIN` | Acceso total: gestión de usuarios, configuración del sistema |
| `OPERARIO` | Gestión operativa: zonas, plantas, sensores, ventas |
| `VISUALIZADOR` | Solo lectura: consulta de datos sin modificaciones |

**Relaciones:**
- `usuarios` 1 → N `ventas` (a través de `usuario_id` en `ventas`)

---

## 3. plantas

**Descripción:** Planta cultivada dentro del invernadero, trazable por número de lote.  
**Tabla BD:** `plantas`  
**Clase Java:** `com.greencore.model.Planta`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único de la planta |
| `nombre` | `nombre` | `String` | `VARCHAR(150)` | No | No | — | min=2, max=150 | Nombre común de la planta |
| `especie` | `especie` | `String` | `VARCHAR(200)` | No | No | — | min=2, max=200 | Nombre científico de la especie |
| `lote` | `lote` | `String` | `VARCHAR(50)` | No | Sí | Auto | patrón `LOT-{AÑO}-{SEQ}` | Código de lote generado automáticamente |
| `cantidad` | `cantidad` | `Integer` | `INTEGER` | No | No | — | min=0 | Unidades disponibles en inventario |
| `precio` | `precio` | `BigDecimal` | `NUMERIC(10,2)` | No | No | — | min=0.0 | Precio unitario de venta en COP |
| `estado` | `estado` | `Enum(EstadoPlanta)` | `VARCHAR(30)` | No | No | `SEMILLA` | valores enum | Estado actual del ciclo de vida |
| `fechaSiembra` | `fecha_siembra` | `LocalDate` | `DATE` | No | No | — | — | Fecha en que se sembró o germinó |
| `fechaEstimadaVenta` | `fecha_estimada_venta` | `LocalDate` | `DATE` | Sí | No | — | — | Fecha estimada de disponibilidad para venta |
| `descripcion` | `descripcion` | `String` | `TEXT` | Sí | No | — | max=500 | Notas de cuidado y características |
| `imagenUrl` | `imagen_url` | `String` | `TEXT` | Sí | No | — | URL válida | URL de imagen representativa |
| `zona_id` | `zona_id` | `Zona (FK)` | `BIGINT` | No | No | — | FK → zonas.id | Zona del invernadero donde está ubicada |
| `creadoEn` | `creado_en` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de creación del registro |

**Estados del ciclo de vida:**
| Estado | Descripción |
|---|---|
| `SEMILLA` | Semilla recién sembrada |
| `GERMINANDO` | En proceso de germinación |
| `CRECIMIENTO` | En etapa de crecimiento activo |
| `LISTA_VENTA` | Lista para ser comercializada |
| `VENDIDA` | Ya comercializada (stock agotado) |
| `BAJA` | Retirada por enfermedad, muerte o descarte |

**Relaciones:**
- `plantas` N → 1 `zonas` (FK: `zona_id`)
- `plantas` 1 → N `ventas` (a través de `planta_id` en `ventas`)

---

## 4. sensores

**Descripción:** Sensor físico instalado en una zona. Registra lecturas periódicas automáticamente.  
**Tabla BD:** `sensores`  
**Clase Java:** `com.greencore.model.Sensor`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único del sensor |
| `codigo` | `codigo` | `String` | `VARCHAR(50)` | No | Sí | — | formato `SNS-TIPO-NNN` | Código único de identificación del sensor |
| `tipo` | `tipo` | `Enum(TipoSensor)` | `VARCHAR(30)` | No | No | — | valores enum | Tipo de magnitud que mide el sensor |
| `valorActual` | `valor_actual` | `Double` | `DOUBLE PRECISION` | Sí | No | — | Actualizado con cada lectura | Última lectura registrada |
| `unidad` | `unidad` | `String` | `VARCHAR(20)` | No | No | — | Ej: °C, %, lux | Unidad de medida del sensor |
| `umbralMinimo` | `umbral_minimo` | `Double` | `DOUBLE PRECISION` | No | No | — | — | Valor mínimo aceptable; por debajo genera alerta |
| `umbralMaximo` | `umbral_maximo` | `Double` | `DOUBLE PRECISION` | No | No | — | — | Valor máximo aceptable; por encima genera alerta |
| `estado` | `estado` | `Enum(EstadoSensor)` | `VARCHAR(20)` | No | No | `ACTIVO` | valores enum | Estado operativo del sensor |
| `ultimaLectura` | `ultima_lectura` | `LocalDateTime` | `TIMESTAMP` | Sí | No | — | Actualizado automáticamente | Timestamp de la última lectura registrada |
| `zona_id` | `zona_id` | `Zona (FK)` | `BIGINT` | No | No | — | FK → zonas.id | Zona donde está instalado el sensor |
| `creadoEn` | `creado_en` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de creación del registro |

**Tipos de sensor:**
| Tipo | Unidad típica |
|---|---|
| `TEMPERATURA` | °C |
| `HUMEDAD` | % |
| `LUMINOSIDAD` | lux |
| `CO2` | ppm |
| `PH_SUELO` | pH |

**Relaciones:**
- `sensores` N → 1 `zonas` (FK: `zona_id`)
- `sensores` 1 → N `lecturas_sensor` (a través de `sensor_id`)
- `sensores` 1 → N `alertas` (a través de `sensor_id`)

---

## 5. lecturas_sensor

**Descripción:** Registro histórico de cada lectura de un sensor. Se inserta automáticamente por el sistema cada 5 minutos.  
**Tabla BD:** `lecturas_sensor`  
**Clase Java:** `com.greencore.model.LecturaSensor`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único de la lectura |
| `valor` | `valor` | `Double` | `DOUBLE PRECISION` | No | No | — | — | Valor registrado por el sensor |
| `fueraDeRango` | `fuera_de_rango` | `Boolean` | `BOOLEAN` | No | No | `false` | Calculado automáticamente | `true` si el valor supera los umbrales del sensor |
| `timestamp` | `timestamp` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora exacta de la lectura |
| `sensor_id` | `sensor_id` | `Sensor (FK)` | `BIGINT` | No | No | — | FK → sensores.id | Sensor que generó la lectura |

**Reglas de negocio:**
- `fueraDeRango = true` cuando `valor < sensor.umbralMinimo` o `valor > sensor.umbralMaximo`
- Al insertar una lectura con `fueraDeRango = true`, el sistema crea automáticamente un registro en `alertas`

**Relaciones:**
- `lecturas_sensor` N → 1 `sensores` (FK: `sensor_id`)

---

## 6. alertas

**Descripción:** Alerta generada automáticamente cuando un sensor registra un valor fuera de rango. Los niveles CRITICO disparan notificación por correo Gmail.  
**Tabla BD:** `alertas`  
**Clase Java:** `com.greencore.model.Alerta`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único de la alerta |
| `mensaje` | `mensaje` | `String` | `TEXT` | No | No | — | Generado por sistema | Descripción legible del evento que generó la alerta |
| `nivel` | `nivel` | `Enum(NivelAlerta)` | `VARCHAR(20)` | No | No | `ADVERTENCIA` | valores enum | Severidad de la alerta |
| `leida` | `leida` | `Boolean` | `BOOLEAN` | No | No | `false` | — | `true` si un usuario ya revisó la alerta |
| `correoEnviado` | `correo_enviado` | `Boolean` | `BOOLEAN` | No | No | `false` | — | `true` si se envió notificación Gmail |
| `valorRegistrado` | `valor_registrado` | `Double` | `DOUBLE PRECISION` | No | No | — | — | Valor exacto que disparó la alerta |
| `timestamp` | `timestamp` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de generación de la alerta |
| `sensor_id` | `sensor_id` | `Sensor (FK)` | `BIGINT` | No | No | — | FK → sensores.id | Sensor que originó la alerta |

**Niveles de alerta:**
| Nivel | Condición | Acción automática |
|---|---|---|
| `INFO` | Valor en rango pero cercano al límite | Sin acción |
| `ADVERTENCIA` | Valor fuera de rango moderado | Registro en sistema |
| `CRITICO` | Valor fuera de rango severo | Envío de correo Gmail |

**Relaciones:**
- `alertas` N → 1 `sensores` (FK: `sensor_id`)

---

## 7. clientes

**Descripción:** Cliente comprador de plantas del invernadero.  
**Tabla BD:** `clientes`  
**Clase Java:** `com.greencore.model.Cliente`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único del cliente |
| `nombre` | `nombre` | `String` | `VARCHAR(150)` | No | No | — | min=2, max=150 | Nombre completo o razón social |
| `email` | `email` | `String` | `VARCHAR(255)` | No | Sí | — | formato email | Correo electrónico de contacto |
| `telefono` | `telefono` | `String` | `VARCHAR(20)` | Sí | No | — | — | Número de teléfono de contacto |
| `ciudad` | `ciudad` | `String` | `VARCHAR(100)` | Sí | No | — | — | Ciudad de ubicación del cliente |
| `activo` | `activo` | `Boolean` | `BOOLEAN` | No | No | `true` | — | Indica si el cliente puede realizar compras |
| `creadoEn` | `creado_en` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de creación del registro |

**Relaciones:**
- `clientes` 1 → N `ventas` (a través de `cliente_id` en `ventas`)

---

## 8. ventas

**Descripción:** Registro de venta de plantas a un cliente. Descuenta stock automáticamente al crear y lo restaura al anular.  
**Tabla BD:** `ventas`  
**Clase Java:** `com.greencore.model.Venta`

| Campo | Columna BD | Tipo Java | Tipo BD | Nulo | Único | Default | Restricciones | Descripción |
|---|---|---|---|---|---|---|---|---|
| `id` | `id` | `Long` | `BIGSERIAL` | No | Sí (PK) | Auto | PK, generado | Identificador único de la venta |
| `numeroFactura` | `numero_factura` | `String` | `VARCHAR(30)` | No | Sí | Auto | patrón `FAC-{AÑO}-{SEQ}` | Número de factura generado automáticamente |
| `cantidad` | `cantidad` | `Integer` | `INTEGER` | No | No | — | min=1 | Unidades de plantas vendidas |
| `precioUnitario` | `precio_unitario` | `BigDecimal` | `NUMERIC(10,2)` | No | No | — | min=0.0, copiado de planta | Precio por unidad al momento de la venta |
| `total` | `total` | `BigDecimal` | `NUMERIC(12,2)` | No | No | Calculado | `cantidad × precioUnitario` | Valor total de la transacción |
| `estado` | `estado` | `Enum(EstadoVenta)` | `VARCHAR(20)` | No | No | `PENDIENTE` | valores enum | Estado actual de la venta |
| `notas` | `notas` | `String` | `TEXT` | Sí | No | — | — | Observaciones adicionales de la venta |
| `fecha` | `fecha` | `LocalDateTime` | `TIMESTAMP` | No | No | Automático | Generado por sistema | Fecha y hora de registro de la venta |
| `planta_id` | `planta_id` | `Planta (FK)` | `BIGINT` | No | No | — | FK → plantas.id | Planta comercializada |
| `cliente_id` | `cliente_id` | `Cliente (FK)` | `BIGINT` | No | No | — | FK → clientes.id | Cliente que realizó la compra |
| `usuario_id` | `usuario_id` | `Usuario (FK)` | `BIGINT` | No | No | — | FK → usuarios.id | Usuario del sistema que registró la venta |

**Estados de venta:**
| Estado | Descripción | Efecto en stock |
|---|---|---|
| `PENDIENTE` | Venta registrada, pendiente de confirmación | Stock descontado |
| `COMPLETADA` | Venta confirmada y entregada | Stock permanece descontado |
| `ANULADA` | Venta cancelada | Stock restaurado automáticamente |

**Relaciones:**
- `ventas` N → 1 `plantas` (FK: `planta_id`)
- `ventas` N → 1 `clientes` (FK: `cliente_id`)
- `ventas` N → 1 `usuarios` (FK: `usuario_id`)
