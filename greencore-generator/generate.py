import json
import os
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR.parent / "modelo.json"
OUTPUT_DIR = BASE_DIR / "generated"
TEMPLATE_DIR = BASE_DIR / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

def load_model():
    with open(MODEL_PATH, encoding="utf-8") as f:
        return json.load(f)

JAVA_TYPE_MAP = {
    "Long": "Long",
    "String": "String",
    "Integer": "Integer",
    "Double": "Double",
    "Boolean": "Boolean",
    "BigDecimal": "BigDecimal",
    "LocalDateTime": "LocalDateTime",
    "LocalDate": "LocalDate",
}

ENUM_TYPES = {"Enum",}


def sanitize(field):
    field = dict(field)
    field["java_type"] = JAVA_TYPE_MAP.get(field["type"], field["type"])
    field["column_name"] = field.get("name")
    field["nullable"] = field.get("nullable", True)
    field["unique"] = field.get("unique", False)
    field["primary_key"] = field.get("primary_key", False)
    field["generated"] = field.get("generated", False)
    field["is_enum"] = field.get("type") == "Enum"
    field["is_relation"] = "relation" in field
    field["join_column"] = field.get("join_column")
    field["default_value"] = field.get("default")
    field["computed"] = field.get("computed", False)
    field["show_in_form"] = field.get("show_in_form", True)
    field["show_in_table"] = field.get("show_in_table", True)
    field["field_name"] = field["name"]
    if field["is_relation"]:
        field["java_type"] = field["type"]
    return field


def build_entity_context(entity, project):
    fields = [sanitize(field) for field in entity.get("fields", [])]
    return {
        "project": project,
        "entity": entity,
        "fields": fields,
        "package": project["base_package"],
        "base_url": project["base_url"].rstrip("/"),
        "class_name": entity["name"],
        "table_name": entity["table"],
        "endpoints": entity.get("endpoints", []),
    }


def render_template(template_name, context, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = env.get_template(template_name)
    output_text = template.render(context)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    print(f"Generado: {output_path}")


def _s(v):
    """Escape and quote a value for SQL."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    return str(v)


def generate_seed_sql(model):
    seed = model.get("seed_data", {})
    if not seed:
        print("No hay seed_data en modelo.json, omitiendo generacion de seed.")
        return

    lines = [
        "-- GreenCore Seed Data",
        "-- Generado automaticamente desde modelo.json",
        "-- Idempotente: ON CONFLICT DO NOTHING / WHERE NOT EXISTS",
        "",
        "-- ZONAS",
    ]

    for z in seed.get("zonas", []):
        lines.append(
            f"INSERT INTO zonas (nombre, descripcion, capacidad_maxima, temperatura_minima, temperatura_maxima, "
            f"humedad_minima, humedad_maxima, activa, creado_en) VALUES ("
            f"{_s(z['nombre'])}, {_s(z.get('descripcion'))}, {z['capacidadMaxima']}, "
            f"{z['temperaturaMinima']}, {z['temperaturaMaxima']}, {z['humedadMinima']}, "
            f"{z['humedadMaxima']}, {_s(z['activa'])}, NOW()) ON CONFLICT (nombre) DO NOTHING;"
        )

    lines += ["", "-- CLIENTES"]
    for c in seed.get("clientes", []):
        lines.append(
            f"INSERT INTO clientes (nombre, email, telefono, ciudad, activo, creado_en) VALUES ("
            f"{_s(c['nombre'])}, {_s(c['email'])}, {_s(c.get('telefono'))}, "
            f"{_s(c.get('ciudad'))}, {_s(c['activo'])}, NOW()) ON CONFLICT (email) DO NOTHING;"
        )

    lines += ["", "-- SENSORES"]
    for s in seed.get("sensores", []):
        va = s.get("valorActual")
        va_sql = str(va) if va is not None else "NULL"
        ul_sql = "NOW()" if va is not None else "NULL"
        lines.append(
            f"INSERT INTO sensores (codigo, tipo, valor_actual, unidad, umbral_minimo, umbral_maximo, "
            f"estado, ultima_lectura, zona_id, creado_en) VALUES ("
            f"{_s(s['codigo'])}, {_s(s['tipo'])}, {va_sql}, {_s(s['unidad'])}, "
            f"{s['umbralMinimo']}, {s['umbralMaximo']}, {_s(s['estado'])}, {ul_sql}, "
            f"(SELECT id FROM zonas WHERE nombre = {_s(s['zona_ref'])}), NOW()) "
            f"ON CONFLICT (codigo) DO NOTHING;"
        )

    lines += ["", "-- PLANTAS"]
    for p in seed.get("plantas", []):
        fev = _s(p.get("fechaEstimadaVenta"))
        lines.append(
            f"INSERT INTO plantas (nombre, especie, lote, cantidad, precio, estado, "
            f"fecha_siembra, fecha_estimada_venta, descripcion, imagen_url, zona_id, creado_en) VALUES ("
            f"{_s(p['nombre'])}, {_s(p['especie'])}, {_s(p['lote'])}, {p['cantidad']}, "
            f"{p['precio']}, {_s(p['estado'])}, {_s(p['fechaSiembra'])}, {fev}, "
            f"{_s(p.get('descripcion'))}, NULL, "
            f"(SELECT id FROM zonas WHERE nombre = {_s(p['zona_ref'])}), NOW()) "
            f"ON CONFLICT (lote) DO NOTHING;"
        )

    lines += ["", "-- LECTURAS SENSOR (solo si la tabla esta vacia)"]
    for l in seed.get("lecturas_sensor", []):
        lines.append(
            f"INSERT INTO lecturas_sensor (valor, fuera_de_rango, \"timestamp\", sensor_id) "
            f"SELECT {l['valor']}, {_s(l['fueraDeRango'])}, NOW(), s.id "
            f"FROM sensores s WHERE s.codigo = {_s(l['sensor_ref'])} "
            f"AND NOT EXISTS (SELECT 1 FROM lecturas_sensor);"
        )

    lines += ["", "-- ALERTAS (solo si la tabla esta vacia)"]
    for a in seed.get("alertas", []):
        lines.append(
            f"INSERT INTO alertas (mensaje, nivel, leida, correo_enviado, valor_registrado, \"timestamp\", sensor_id) "
            f"SELECT {_s(a['mensaje'])}, {_s(a['nivel'])}, {_s(a['leida'])}, "
            f"{_s(a['correoEnviado'])}, {a['valorRegistrado']}, NOW(), s.id "
            f"FROM sensores s WHERE s.codigo = {_s(a['sensor_ref'])} "
            f"AND NOT EXISTS (SELECT 1 FROM alertas);"
        )

    lines.append("")
    sql = "\n".join(lines)

    # data.sql → Spring Boot lo ejecuta automaticamente al arrancar
    data_sql = BASE_DIR.parent / "backend" / "src" / "main" / "resources" / "data.sql"
    data_sql.parent.mkdir(parents=True, exist_ok=True)
    with open(data_sql, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Generado: {data_sql}")

    # seed.sql → para ejecutar manualmente en pgAdmin
    docs_sql = BASE_DIR.parent / "docs" / "seed.sql"
    docs_sql.parent.mkdir(parents=True, exist_ok=True)
    with open(docs_sql, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Generado: {docs_sql}")


def generate_appirest_collection(entities, project):
    collection = {
        "info": {
            "name": f"{project['name']} Appirest Collection",
            "description": project["description"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }
    for entity in entities:
        base = project["base_url"] + "/" + entity["table"]
        collection["item"].append({
            "name": f"{entity['name']} - Listar",
            "request": {
                "method": "GET",
                "header": [],
                "url": {"raw": "{{base_url}}" + base, "host": ["{{base_url}}"], "path": [project["base_url"].strip("/"), entity["table"]]},
            },
        })
    output = OUTPUT_DIR / "appirest_collection.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    print(f"Generado: {output}")


def generate_i18n(model):
    """
    Genera los archivos messages.properties (ES) y messages_en.properties (EN)
    a partir del modelo.json. Estos archivos son consumidos por Spring MessageSource.
    Se escriben en:
      - backend/src/main/resources/messages.properties
      - backend/src/main/resources/messages_en.properties
    """
    entities = model.get("entities", [])
    project  = model["project"]

    # ── Traducciones de labels por entidad ────────────────────────────────────
    LABELS_ES = {
        "zona":    {"nombre":"Nombre","descripcion":"Descripción","capacidadMaxima":"Capacidad máxima",
                    "temperaturaMinima":"Temperatura mínima","temperaturaMaxima":"Temperatura máxima",
                    "humedadMinima":"Humedad mínima","humedadMaxima":"Humedad máxima","activa":"Activa",
                    "creadoEn":"Fecha de creación"},
        "usuario": {"email":"Correo electrónico","nombre":"Nombre","fotoPerfil":"Foto de perfil",
                    "rol":"Rol","provider":"Proveedor","providerId":"ID de proveedor",
                    "activo":"Activo","ultimoAcceso":"Último acceso","creadoEn":"Fecha de creación"},
        "planta":  {"nombre":"Nombre","especie":"Especie","lote":"Lote","cantidad":"Cantidad",
                    "precio":"Precio","estado":"Estado","fechaSiembra":"Fecha de siembra",
                    "fechaEstimadaVenta":"Fecha estimada de venta","descripcion":"Descripción",
                    "imagenUrl":"Imagen","zona":"Zona","creadoEn":"Fecha de creación"},
        "sensor":  {"codigo":"Código","tipo":"Tipo","valorActual":"Valor actual","unidad":"Unidad",
                    "umbralMinimo":"Umbral mínimo","umbralMaximo":"Umbral máximo","estado":"Estado",
                    "ultimaLectura":"Última lectura","zona":"Zona","creadoEn":"Fecha de creación"},
        "lectura": {"valor":"Valor","fueraDeRango":"Fuera de rango","timestamp":"Fecha/hora",
                    "sensor":"Sensor"},
        "alerta":  {"mensaje":"Mensaje","nivel":"Nivel","leida":"Leída","correoEnviado":"Correo enviado",
                    "valorRegistrado":"Valor registrado","timestamp":"Fecha/hora","sensor":"Sensor"},
        "cliente": {"nombre":"Nombre","email":"Correo electrónico","telefono":"Teléfono",
                    "ciudad":"Ciudad","activo":"Activo","creadoEn":"Fecha de creación"},
        "venta":   {"numeroFactura":"N° Factura","cantidad":"Cantidad","precioUnitario":"Precio unitario",
                    "total":"Total","estado":"Estado","notas":"Notas","fecha":"Fecha",
                    "planta":"Planta","cliente":"Cliente","registradoPor":"Registrado por"},
    }

    LABELS_EN = {
        "zona":    {"nombre":"Name","descripcion":"Description","capacidadMaxima":"Max capacity",
                    "temperaturaMinima":"Min temperature","temperaturaMaxima":"Max temperature",
                    "humedadMinima":"Min humidity","humedadMaxima":"Max humidity","activa":"Active",
                    "creadoEn":"Created at"},
        "usuario": {"email":"Email","nombre":"Name","fotoPerfil":"Profile picture",
                    "rol":"Role","provider":"Provider","providerId":"Provider ID",
                    "activo":"Active","ultimoAcceso":"Last access","creadoEn":"Created at"},
        "planta":  {"nombre":"Name","especie":"Species","lote":"Batch","cantidad":"Quantity",
                    "precio":"Price","estado":"Status","fechaSiembra":"Sowing date",
                    "fechaEstimadaVenta":"Estimated sale date","descripcion":"Description",
                    "imagenUrl":"Image","zona":"Zone","creadoEn":"Created at"},
        "sensor":  {"codigo":"Code","tipo":"Type","valorActual":"Current value","unidad":"Unit",
                    "umbralMinimo":"Min threshold","umbralMaximo":"Max threshold","estado":"Status",
                    "ultimaLectura":"Last reading","zona":"Zone","creadoEn":"Created at"},
        "lectura": {"valor":"Value","fueraDeRango":"Out of range","timestamp":"Timestamp",
                    "sensor":"Sensor"},
        "alerta":  {"mensaje":"Message","nivel":"Level","leida":"Read","correoEnviado":"Email sent",
                    "valorRegistrado":"Recorded value","timestamp":"Timestamp","sensor":"Sensor"},
        "cliente": {"nombre":"Name","email":"Email","telefono":"Phone",
                    "ciudad":"City","activo":"Active","creadoEn":"Created at"},
        "venta":   {"numeroFactura":"Invoice No.","cantidad":"Quantity","precioUnitario":"Unit price",
                    "total":"Total","estado":"Status","notas":"Notes","fecha":"Date",
                    "planta":"Plant","cliente":"Client","registradoPor":"Registered by"},
    }

    # ── Nombres de entidades ──────────────────────────────────────────────────
    ENTITY_NAMES_ES = {
        "Zona":"Zona","Planta":"Planta","Sensor":"Sensor","LecturaSensor":"Lectura de sensor",
        "Alerta":"Alerta","Cliente":"Cliente","Venta":"Venta","Usuario":"Usuario",
    }
    ENTITY_NAMES_EN = {
        "Zona":"Zone","Planta":"Plant","Sensor":"Sensor","LecturaSensor":"Sensor reading",
        "Alerta":"Alert","Cliente":"Client","Venta":"Sale","Usuario":"User",
    }

    def build_props(labels_map, entity_names, lang):
        lines = [
            f"# GreenCore — messages_{lang}.properties" if lang != "es" else "# GreenCore — messages.properties",
            f"# Generado automaticamente desde modelo.json — NO editar manualmente",
            f"# Idioma: {'Espanol (por defecto)' if lang == 'es' else 'English'}",
            "",
            "# ── Errores comunes ─────────────────────────────────────────────────",
        ]

        if lang == "es":
            lines += [
                "error.notFound={0} no encontrado con ID: {1}",
                "error.badRequest=Solicitud invalida: {0}",
                "error.conflict=Ya existe un registro con ese valor: {0}",
                "error.stockInsuficiente=Stock insuficiente. Disponible\\: {0}, solicitado\\: {1}",
                "error.clienteConVentas=El cliente tiene ventas asociadas y no puede eliminarse",
                "error.sensorFalla=El sensor esta en estado FALLA y no acepta lecturas",
                "error.tokenExpirado=Token expirado o invalido. Por favor inicia sesion nuevamente",
                "error.accesoDenegado=No tienes permisos para realizar esta accion",
                "",
                "# ── Mensajes de exito ───────────────────────────────────────────────",
                "success.created={0} creado exitosamente",
                "success.updated={0} actualizado exitosamente",
                "success.deleted={0} eliminado exitosamente",
                "success.lecturaRegistrada=Lectura registrada. Sensor\\: {0}, Valor\\: {1}",
                "success.alertaLeida=Alerta marcada como leida",
                "",
                "# ── Alertas automaticas (cuerpo del correo Gmail) ───────────────────",
                "alerta.email.subject=[GreenCore] Alerta {0} — Sensor {1}",
                "alerta.email.body=Sensor\\: {0}\\nZona\\: {1}\\nValor registrado\\: {2} {3}\\nRango permitido\\: {4} — {5}\\nFecha\\: {6}",
                "alerta.critico=Sensor {0} supero umbral critico: {1} (rango: {2}-{3})",
                "alerta.advertencia=Sensor {0} registro valor fuera de rango: {1}",
                "",
                "# ── Validacion de campos ────────────────────────────────────────────",
                "validation.required={0} es obligatorio",
                "validation.minLength={0} debe tener al menos {1} caracteres",
                "validation.maxLength={0} no puede superar {1} caracteres",
                "validation.minValue={0} debe ser mayor o igual a {1}",
                "validation.maxValue={0} no puede superar {1}",
                "validation.emailInvalido=El correo electronico no tiene un formato valido",
                "validation.unicidad={0} ya esta registrado en el sistema",
            ]
        else:
            lines += [
                "error.notFound={0} not found with ID: {1}",
                "error.badRequest=Invalid request: {0}",
                "error.conflict=A record with that value already exists: {0}",
                "error.stockInsuficiente=Insufficient stock. Available\\: {0}, requested\\: {1}",
                "error.clienteConVentas=The client has associated sales and cannot be deleted",
                "error.sensorFalla=Sensor is in FALLA state and does not accept readings",
                "error.tokenExpirado=Token expired or invalid. Please sign in again",
                "error.accesoDenegado=You do not have permission to perform this action",
                "",
                "# ── Success messages ────────────────────────────────────────────────",
                "success.created={0} created successfully",
                "success.updated={0} updated successfully",
                "success.deleted={0} deleted successfully",
                "success.lecturaRegistrada=Reading registered. Sensor\\: {0}, Value\\: {1}",
                "success.alertaLeida=Alert marked as read",
                "",
                "# ── Automatic alerts (Gmail body) ───────────────────────────────────",
                "alerta.email.subject=[GreenCore] {0} Alert — Sensor {1}",
                "alerta.email.body=Sensor\\: {0}\\nZone\\: {1}\\nRecorded value\\: {2} {3}\\nAllowed range\\: {4} — {5}\\nDate\\: {6}",
                "alerta.critico=Sensor {0} exceeded critical threshold: {1} (range: {2}-{3})",
                "alerta.advertencia=Sensor {0} recorded out-of-range value: {1}",
                "",
                "# ── Field validation ────────────────────────────────────────────────",
                "validation.required={0} is required",
                "validation.minLength={0} must have at least {1} characters",
                "validation.maxLength={0} cannot exceed {1} characters",
                "validation.minValue={0} must be greater than or equal to {1}",
                "validation.maxValue={0} cannot exceed {1}",
                "validation.emailInvalido=Email address format is invalid",
                "validation.unicidad={0} is already registered in the system",
            ]

        # Nombres de entidades
        lines += ["", "# ── Nombres de entidades ───────────────────────────────────────────"]
        for en, label in entity_names.items():
            lines.append(f"entity.{en.lower()}={label}")

        # Labels de campos por entidad
        for entity_key, fields in labels_map.items():
            lines += ["", f"# ── {entity_key.capitalize()} ─────────────────────────────────────────────"]
            for field_key, label in fields.items():
                lines.append(f"{entity_key}.{field_key}={label}")

        # Roles
        lines += ["", "# ── Roles ───────────────────────────────────────────────────────────"]
        if lang == "es":
            lines += [
                "role.ADMIN=Administrador",
                "role.OPERARIO=Operario",
                "role.VISUALIZADOR=Visualizador",
            ]
        else:
            lines += [
                "role.ADMIN=Administrator",
                "role.OPERARIO=Operator",
                "role.VISUALIZADOR=Viewer",
            ]

        # Estados de enums leidos desde modelo.json
        lines += ["", "# ── Estados (enumeraciones) ─────────────────────────────────────────"]
        ENUM_TRANS = {
            "es": {
                "SEMILLA":"Semilla","GERMINANDO":"Germinando","CRECIMIENTO":"Crecimiento",
                "LISTA_VENTA":"Lista para venta","VENDIDA":"Vendida","BAJA":"Baja",
                "ACTIVO":"Activo","INACTIVO":"Inactivo","FALLA":"Falla","CALIBRANDO":"Calibrando",
                "TEMPERATURA":"Temperatura","HUMEDAD":"Humedad","LUMINOSIDAD":"Luminosidad",
                "CO2":"CO2","PH_SUELO":"pH del suelo",
                "INFO":"Información","ADVERTENCIA":"Advertencia","CRITICO":"Crítico",
                "PENDIENTE":"Pendiente","COMPLETADA":"Completada","ANULADA":"Anulada",
                "ADMIN":"Administrador","OPERARIO":"Operario","VISUALIZADOR":"Visualizador",
            },
            "en": {
                "SEMILLA":"Seed","GERMINANDO":"Germinating","CRECIMIENTO":"Growing",
                "LISTA_VENTA":"Ready for sale","VENDIDA":"Sold","BAJA":"Discharged",
                "ACTIVO":"Active","INACTIVO":"Inactive","FALLA":"Fault","CALIBRANDO":"Calibrating",
                "TEMPERATURA":"Temperature","HUMEDAD":"Humidity","LUMINOSIDAD":"Luminosity",
                "CO2":"CO2","PH_SUELO":"Soil pH",
                "INFO":"Info","ADVERTENCIA":"Warning","CRITICO":"Critical",
                "PENDIENTE":"Pending","COMPLETADA":"Completed","ANULADA":"Cancelled",
                "ADMIN":"Administrator","OPERARIO":"Operator","VISUALIZADOR":"Viewer",
            },
        }
        for val, label in ENUM_TRANS[lang].items():
            lines.append(f"enum.{val}={label}")

        return "\n".join(lines) + "\n"

    resources = BASE_DIR.parent / "backend" / "src" / "main" / "resources"
    resources.mkdir(parents=True, exist_ok=True)

    es_path = resources / "messages.properties"
    en_path = resources / "messages_en.properties"

    with open(es_path, "w", encoding="utf-8") as f:
        f.write(build_props(LABELS_ES, ENTITY_NAMES_ES, "es"))
    print(f"Generado: {es_path}")

    with open(en_path, "w", encoding="utf-8") as f:
        f.write(build_props(LABELS_EN, ENTITY_NAMES_EN, "en"))
    print(f"Generado: {en_path}")


def main():
    model = load_model()
    project = model["project"]
    entities = model.get("entities", [])

    for entity in entities:
        context = build_entity_context(entity, project)
        render_template("entity.java.j2", context, OUTPUT_DIR / "backend" / "src" / "main" / "java" / project["base_package"].replace(".", "/") / "model" / f"{entity['name']}.java")
        render_template("repository.java.j2", context, OUTPUT_DIR / "backend" / "src" / "main" / "java" / project["base_package"].replace(".", "/") / "repository" / f"{entity['name']}Repository.java")
        render_template("service.java.j2", context, OUTPUT_DIR / "backend" / "src" / "main" / "java" / project["base_package"].replace(".", "/") / "service" / f"{entity['name']}Service.java")
        render_template("controller.java.j2", context, OUTPUT_DIR / "backend" / "src" / "main" / "java" / project["base_package"].replace(".", "/") / "controller" / f"{entity['name']}Controller.java")

        if entity.get("generate_frontend", False):
            render_template("component.jsx.j2", context, OUTPUT_DIR / "frontend" / "src" / "components" / f"{entity['name']}List.jsx")
            render_template("service.js.j2", context, OUTPUT_DIR / "frontend" / "src" / "services" / f"{entity['name'].lower()}Service.js")

        if entity.get("generate_tests", False):
            render_template("test_junit.java.j2", context, OUTPUT_DIR / "backend" / "src" / "test" / "java" / project["base_package"].replace(".", "/") / f"{entity['name']}ControllerTest.java")
            render_template("test_api.py.j2", context, OUTPUT_DIR / "backend" / "tests" / f"test_{entity['name'].lower()}_api.py")

    generate_appirest_collection(entities, project)
    generate_seed_sql(model)
    generate_i18n(model)
    print("Generación completada.")


if __name__ == "__main__":
    main()
