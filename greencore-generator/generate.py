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
    print("Generación completada.")


if __name__ == "__main__":
    main()
