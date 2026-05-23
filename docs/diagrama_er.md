# Diagrama Entidad-Relación — GreenCore

**Sistema:** GreenCore — Gestión integral de invernadero  
**Base de datos:** PostgreSQL  
**Versión:** 1.0.0  

---

```mermaid
erDiagram

    ZONAS {
        BIGSERIAL   id              PK
        VARCHAR100  nombre          UK  "NOT NULL"
        TEXT        descripcion
        INTEGER     capacidadMaxima         "NOT NULL"
        DOUBLE      temperaturaMinima       "NOT NULL"
        DOUBLE      temperaturaMaxima       "NOT NULL"
        DOUBLE      humedadMinima           "NOT NULL"
        DOUBLE      humedadMaxima           "NOT NULL"
        BOOLEAN     activa                  "NOT NULL DEFAULT true"
        TIMESTAMP   creadoEn                "NOT NULL"
    }

    USUARIOS {
        BIGSERIAL   id          PK
        VARCHAR255  email       UK  "NOT NULL"
        VARCHAR150  nombre          "NOT NULL"
        TEXT        fotoPerfil
        VARCHAR30   rol             "NOT NULL DEFAULT OPERARIO"
        VARCHAR30   provider        "NOT NULL DEFAULT GOOGLE"
        VARCHAR255  providerId  UK  "NOT NULL"
        BOOLEAN     activo          "NOT NULL DEFAULT true"
        TIMESTAMP   ultimoAcceso
        TIMESTAMP   creadoEn        "NOT NULL"
    }

    PLANTAS {
        BIGSERIAL   id                  PK
        VARCHAR150  nombre                  "NOT NULL"
        VARCHAR200  especie                 "NOT NULL"
        VARCHAR50   lote                UK  "NOT NULL"
        INTEGER     cantidad                "NOT NULL"
        NUMERIC102  precio                  "NOT NULL"
        VARCHAR30   estado                  "NOT NULL DEFAULT SEMILLA"
        DATE        fechaSiembra            "NOT NULL"
        DATE        fechaEstimadaVenta
        TEXT        descripcion
        TEXT        imagenUrl
        BIGINT      zona_id             FK  "NOT NULL"
        TIMESTAMP   creadoEn                "NOT NULL"
    }

    SENSORES {
        BIGSERIAL   id              PK
        VARCHAR50   codigo          UK  "NOT NULL"
        VARCHAR30   tipo                "NOT NULL"
        DOUBLE      valorActual
        VARCHAR20   unidad              "NOT NULL"
        DOUBLE      umbralMinimo        "NOT NULL"
        DOUBLE      umbralMaximo        "NOT NULL"
        VARCHAR20   estado              "NOT NULL DEFAULT ACTIVO"
        TIMESTAMP   ultimaLectura
        BIGINT      zona_id         FK  "NOT NULL"
        TIMESTAMP   creadoEn            "NOT NULL"
    }

    LECTURAS_SENSOR {
        BIGSERIAL   id              PK
        DOUBLE      valor               "NOT NULL"
        BOOLEAN     fueraDeRango        "NOT NULL DEFAULT false"
        TIMESTAMP   timestamp           "NOT NULL"
        BIGINT      sensor_id       FK  "NOT NULL"
    }

    ALERTAS {
        BIGSERIAL   id              PK
        TEXT        mensaje             "NOT NULL"
        VARCHAR20   nivel               "NOT NULL DEFAULT ADVERTENCIA"
        BOOLEAN     leida               "NOT NULL DEFAULT false"
        BOOLEAN     correoEnviado       "NOT NULL DEFAULT false"
        DOUBLE      valorRegistrado     "NOT NULL"
        TIMESTAMP   timestamp           "NOT NULL"
        BIGINT      sensor_id       FK  "NOT NULL"
    }

    CLIENTES {
        BIGSERIAL   id          PK
        VARCHAR150  nombre          "NOT NULL"
        VARCHAR255  email       UK  "NOT NULL"
        VARCHAR20   telefono
        VARCHAR100  ciudad
        BOOLEAN     activo          "NOT NULL DEFAULT true"
        TIMESTAMP   creadoEn        "NOT NULL"
    }

    VENTAS {
        BIGSERIAL   id              PK
        VARCHAR30   numeroFactura   UK  "NOT NULL"
        INTEGER     cantidad            "NOT NULL"
        NUMERIC102  precioUnitario      "NOT NULL"
        NUMERIC122  total               "NOT NULL"
        VARCHAR20   estado              "NOT NULL DEFAULT PENDIENTE"
        TEXT        notas
        TIMESTAMP   fecha               "NOT NULL"
        BIGINT      planta_id       FK  "NOT NULL"
        BIGINT      cliente_id      FK  "NOT NULL"
        BIGINT      usuario_id      FK  "NOT NULL"
    }

    ZONAS        ||--o{ PLANTAS         : "tiene"
    ZONAS        ||--o{ SENSORES        : "contiene"
    SENSORES     ||--o{ LECTURAS_SENSOR : "genera"
    SENSORES     ||--o{ ALERTAS         : "dispara"
    PLANTAS      ||--o{ VENTAS          : "se vende en"
    CLIENTES     ||--o{ VENTAS          : "realiza"
    USUARIOS     ||--o{ VENTAS          : "registra"
```

---

## Resumen de Relaciones

| Tabla origen | Cardinalidad | Tabla destino | FK en tabla destino |
|---|---|---|---|
| `zonas` | 1 → N | `plantas` | `zona_id` |
| `zonas` | 1 → N | `sensores` | `zona_id` |
| `sensores` | 1 → N | `lecturas_sensor` | `sensor_id` |
| `sensores` | 1 → N | `alertas` | `sensor_id` |
| `plantas` | 1 → N | `ventas` | `planta_id` |
| `clientes` | 1 → N | `ventas` | `cliente_id` |
| `usuarios` | 1 → N | `ventas` | `usuario_id` |
