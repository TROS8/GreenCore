"""
GreenCore - Herramienta para agregar UNA historia de usuario a Taiga.
Verifica primero que no exista ya una historia con el mismo titulo.

Uso:
    python add_story.py

    Edita la seccion  NEW_STORY  al final del archivo con los datos de
    la nueva historia, luego ejecuta el script.

Credenciales:
    Configura taiga-client/.env con:
        TAIGA_USERNAME=tu_usuario
        TAIGA_PASSWORD=tu_contrasena
        TAIGA_PROJECT=tros8-greencore   (slug del proyecto)
"""
import os
import sys
import requests
import time
from pathlib import Path

# ── Cargar .env ────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv opcional; acepta variables de entorno del sistema

TAIGA_URL = os.getenv("TAIGA_URL", "https://api.taiga.io")
USERNAME  = os.getenv("TAIGA_USERNAME", "")
PASSWORD  = os.getenv("TAIGA_PASSWORD", "")
SLUG      = os.getenv("TAIGA_PROJECT", "tros8-greencore")

if not USERNAME or not PASSWORD:
    print("ERROR: Configura TAIGA_USERNAME y TAIGA_PASSWORD en .env")
    sys.exit(1)


# ── Autenticar ─────────────────────────────────────────────────────────────────
auth_resp = requests.post(
    f"{TAIGA_URL}/api/v1/auth",
    json={"type": "normal", "username": USERNAME, "password": PASSWORD},
    timeout=10,
)
if auth_resp.status_code != 200:
    print(f"ERROR de autenticacion: HTTP {auth_resp.status_code}")
    sys.exit(1)

TOKEN = auth_resp.json()["auth_token"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
print(f"Autenticado como '{USERNAME}'")


# ── Obtener proyecto ───────────────────────────────────────────────────────────
proj_resp = requests.get(
    f"{TAIGA_URL}/api/v1/projects/by_slug",
    params={"slug": SLUG},
    headers=HEADERS,
    timeout=10,
)
if proj_resp.status_code != 200:
    print(f"ERROR: proyecto '{SLUG}' no encontrado (HTTP {proj_resp.status_code})")
    sys.exit(1)

proj       = proj_resp.json()
PROJECT_ID = proj["id"]
print(f"Proyecto: {proj['name']} (ID: {PROJECT_ID})")


# ── Obtener estados disponibles ────────────────────────────────────────────────
statuses_resp = requests.get(
    f"{TAIGA_URL}/api/v1/userstory-statuses",
    params={"project": PROJECT_ID},
    headers=HEADERS,
    timeout=10,
)
statuses = {s["name"]: s["id"] for s in statuses_resp.json()}

# Mapa conveniente: nombre corto -> ID de estado
STATUS_MAP = {
    "nuevo":       statuses.get("New",         list(statuses.values())[0]),
    "en progreso": statuses.get("In progress", list(statuses.values())[1]),
    "listo":       statuses.get("Ready",       list(statuses.values())[2]),
    "done":        statuses.get("Done",        list(statuses.values())[-1]),
}
print(f"Estados disponibles: {list(statuses.keys())}")


# ── Verificar si ya existe una historia con el mismo titulo ────────────────────
def story_exists(project_id: int, subject: str) -> bool:
    """Devuelve True si ya hay una historia con ese titulo exacto."""
    page = 1
    while True:
        resp = requests.get(
            f"{TAIGA_URL}/api/v1/userstories",
            params={"project": project_id, "page": page, "page_size": 100},
            headers=HEADERS,
            timeout=10,
        )
        if resp.status_code != 200:
            break
        stories = resp.json()
        if not stories:
            break
        for s in stories:
            if s.get("subject", "").strip() == subject.strip():
                return True
        if len(stories) < 100:
            break
        page += 1
    return False


def create_story(project_id: int, subject: str, description: str, status_key: str = "done") -> None:
    """Crea una historia de usuario en Taiga, verificando duplicados primero."""
    status_id = STATUS_MAP.get(status_key.lower(), STATUS_MAP["done"])

    print(f"\nVerificando si ya existe: '{subject}'...")
    if story_exists(project_id, subject):
        print(f"  [OMITIDA] Ya existe una historia con ese titulo.")
        return

    payload = {
        "project":     project_id,
        "subject":     subject,
        "status":      status_id,
        "description": description,
    }
    resp = requests.post(
        f"{TAIGA_URL}/api/v1/userstories",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    if resp.status_code == 201:
        data = resp.json()
        ref  = data.get("ref", "?")
        print(f"  [CREADA] #{ref} - {subject}")
    else:
        print(f"  [ERROR]  HTTP {resp.status_code}: {resp.text[:120]}")


# ==============================================================================
#   EDITA ESTA SECCION PARA AGREGAR UNA NUEVA HISTORIA
#   subject     : titulo de la historia (debe ser unico)
#   description : descripcion con criterios de aceptacion
#   status      : "nuevo" | "en progreso" | "listo" | "done"
# ==============================================================================

NEW_STORY = {
    "subject": "Control de acceso por roles RBAC",
    "status":  "done",
    "description": (
        "Como administrador, quiero que cada rol solo pueda realizar "
        "las acciones que le corresponden.\n\n"
        "Criterios de aceptacion:\n"
        "- [x] ADMIN puede borrar usuarios (DELETE /api/v1/usuarios/**)\n"
        "- [x] ADMIN y OPERARIO pueden crear, editar y eliminar recursos\n"
        "- [x] VISUALIZADOR solo puede hacer peticiones GET\n"
        "- [x] JWT contiene el claim 'role'; JwtFilter lo traduce a ROLE_xxx\n"
        "- [x] Spring Security verifica hasRole() en cada endpoint sensible"
    ),
}

# ==============================================================================

if __name__ == "__main__":
    create_story(
        project_id  = PROJECT_ID,
        subject     = NEW_STORY["subject"],
        description = NEW_STORY["description"],
        status_key  = NEW_STORY["status"],
    )
    print("\nFinalizado.")
