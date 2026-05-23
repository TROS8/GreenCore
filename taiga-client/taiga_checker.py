#!/usr/bin/env python3
"""
GreenCore — Sistema de gestión de invernadero
Taiga Connectivity Checker

Conecta a la API REST de Taiga, lista las user stories del proyecto GreenCore,
valida criterios de aceptación y genera un reporte de trazabilidad.

Uso:
    python taiga_checker.py                   # modo interactivo
    python taiga_checker.py --report html     # genera taiga-report.html
    python taiga_checker.py --report csv      # genera taiga-report.csv
    python taiga_checker.py --ci              # modo CI (exit 1 si hay stories sin completar)

Variables de entorno (o archivo .env):
    TAIGA_URL       URL base de Taiga       (por defecto: https://api.taiga.io)
    TAIGA_USERNAME  Nombre de usuario Taiga
    TAIGA_PASSWORD  Contraseña Taiga
    TAIGA_PROJECT   Slug del proyecto       (por defecto: greencore-invernadero)

@author GreenCore Team
@version 1.0.0
"""

import os
import sys
import io
import json
import argparse
import datetime
from typing import Optional
from pathlib import Path

# Forzar UTF-8 en stdout/stderr para soportar caracteres especiales en cualquier plataforma
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
    from tabulate import tabulate
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] Dependencias no instaladas. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

# ── Cargar variables de entorno desde .env si existe ──────────────────────────
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)

# ── Configuración ─────────────────────────────────────────────────────────────
TAIGA_URL      = os.getenv("TAIGA_URL",      "https://api.taiga.io")
TAIGA_USERNAME = os.getenv("TAIGA_USERNAME", "")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD", "")
TAIGA_PROJECT  = os.getenv("TAIGA_PROJECT",  "tros8-greencore")

API_BASE = f"{TAIGA_URL.rstrip('/')}/api/v1"


# ═══════════════════════════════════════════════════════════════════════════════
# Cliente Taiga REST
# ═══════════════════════════════════════════════════════════════════════════════

class TaigaClient:
    """Cliente REST para la API de Taiga (https://docs.taiga.io/api.html)."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url  = base_url
        self.username  = username
        self.password  = password
        self.token: Optional[str] = None
        self.session   = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        })

    # ── Autenticación ─────────────────────────────────────────────────────────
    def authenticate(self) -> bool:
        """
        Autentica con la API de Taiga y almacena el token de acceso.
        Endpoint: POST /api/v1/auth

        Returns:
            True si la autenticación fue exitosa, False en caso contrario.
        """
        url = f"{self.base_url}/auth"
        payload = {
            "type":     "normal",
            "username": self.username,
            "password": self.password,
        }
        try:
            resp = self.session.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("auth_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"✅ Autenticado en Taiga como '{self.username}'")
                return True
            else:
                print(f"❌ Error de autenticación: HTTP {resp.status_code} — {resp.text[:200]}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ No se pudo conectar a Taiga ({self.base_url})")
            print("   Verifica la URL y la conectividad de red.")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout al conectar con Taiga")
            return False

    # ── Proyecto ──────────────────────────────────────────────────────────────
    def get_project(self, slug: str) -> Optional[dict]:
        """
        Obtiene el proyecto por su slug.
        Endpoint: GET /api/v1/projects/by_slug?slug={slug}

        Args:
            slug: identificador URL del proyecto en Taiga

        Returns:
            Datos del proyecto o None si no se encontró.
        """
        url = f"{self.base_url}/projects/by_slug"
        resp = self.session.get(url, params={"slug": slug}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        print(f"❌ Proyecto '{slug}' no encontrado: HTTP {resp.status_code}")
        return None

    # ── User Stories ──────────────────────────────────────────────────────────
    def get_user_stories(self, project_id: int) -> list[dict]:
        """
        Lista todas las user stories del proyecto.
        Endpoint: GET /api/v1/userstories?project={id}

        Args:
            project_id: ID numérico del proyecto en Taiga

        Returns:
            Lista de user stories.
        """
        url = f"{self.base_url}/userstories"
        resp = self.session.get(url, params={"project": project_id}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        print(f"⚠️  No se pudieron obtener user stories: HTTP {resp.status_code}")
        return []

    # ── Criterios de aceptación ───────────────────────────────────────────────
    def get_story_detail(self, story_id: int) -> Optional[dict]:
        """
        Obtiene el detalle completo de una user story incluyendo criterios de aceptación.
        Endpoint: GET /api/v1/userstories/{id}

        Args:
            story_id: ID de la user story

        Returns:
            Detalle de la story o None.
        """
        url = f"{self.base_url}/userstories/{story_id}"
        resp = self.session.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return None

    # ── Epics ─────────────────────────────────────────────────────────────────
    def get_epics(self, project_id: int) -> list[dict]:
        """
        Lista los epics del proyecto.
        Endpoint: GET /api/v1/epics?project={id}

        Args:
            project_id: ID del proyecto

        Returns:
            Lista de epics.
        """
        url = f"{self.base_url}/epics"
        resp = self.session.get(url, params={"project": project_id}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# Lógica de validación
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_stories(stories: list[dict]) -> dict:
    """
    Analiza las user stories y calcula métricas de completitud.

    Args:
        stories: lista de user stories de Taiga

    Returns:
        Diccionario con métricas y listas clasificadas de stories.
    """
    total    = len(stories)
    done     = [s for s in stories if s.get("is_closed", False)]
    in_prog  = [s for s in stories if not s.get("is_closed", False)
                                    and s.get("status_extra_info", {}).get("name", "").lower()
                                        not in ("new", "ready", "backlog", "")]
    pending  = [s for s in stories if not s.get("is_closed", False)]
    points   = sum(s.get("total_points") or 0 for s in stories)
    done_pts = sum(s.get("total_points") or 0 for s in done)

    return {
        "total":      total,
        "done":       len(done),
        "in_progress": len(in_prog),
        "pending":    len(pending),
        "completion": round(len(done) / total * 100, 1) if total else 0,
        "total_points":  points,
        "done_points":   done_pts,
        "stories_done":   done,
        "stories_pending": pending,
        "all_stories":    stories,
    }


def check_acceptance_criteria(story: dict) -> tuple[bool, list[str]]:
    """
    Extrae y evalúa los criterios de aceptación de una user story.
    Taiga almacena los criterios en el campo 'description' como texto libre.

    Args:
        story: datos de la user story (detalle completo)

    Returns:
        (criterios_definidos: bool, lista_de_criterios: list[str])
    """
    description = story.get("description", "") or ""
    criteria: list[str] = []

    # Buscar líneas que comiencen con patrones de criterio de aceptación
    for line in description.splitlines():
        line = line.strip()
        if line.startswith(("- [ ]", "- [x]", "- [X]", "✓", "✗", "[ ]", "[x]",
                             "AC:", "Criterio", "Given", "When", "Then")):
            criteria.append(line)

    # Si no hay criterios formateados, cualquier contenido no vacío es válido
    if not criteria and description.strip():
        # Tomar primeras 3 líneas no vacías como criterios informales
        criteria = [l.strip() for l in description.splitlines() if l.strip()][:3]

    return bool(criteria), criteria


# ═══════════════════════════════════════════════════════════════════════════════
# Generadores de reporte
# ═══════════════════════════════════════════════════════════════════════════════

def print_console_report(metrics: dict, project: dict) -> None:
    """Imprime el reporte en la consola con formato tabular."""
    sep = "=" * 70
    print()
    print(sep)
    print(f"  GREENCORE -- Reporte Taiga: {project.get('name', TAIGA_PROJECT)}")
    print(f"  Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(sep)

    # -- Resumen --
    print()
    print("RESUMEN")
    summary = [
        ["Total user stories",    metrics["total"]],
        ["[OK] Completadas",      metrics["done"]],
        ["[>>] En progreso",      metrics["in_progress"]],
        ["[--] Pendientes",       metrics["pending"]],
        ["Completitud",           f"{metrics['completion']}%"],
        ["Story points (total)",  metrics["total_points"]],
        ["Story points (done)",   metrics["done_points"]],
    ]
    print(tabulate(summary, tablefmt="grid"))

    # -- Stories completadas --
    if metrics["stories_done"]:
        print()
        print("STORIES COMPLETADAS")
        rows = []
        for s in metrics["stories_done"]:
            ref    = f"#{s.get('ref', '?')}"
            title  = s.get("subject", "")[:55]
            points = s.get("total_points") or "—"
            status = s.get("status_extra_info", {}).get("name", "Cerrada")
            rows.append([ref, title, status, points])
        print(tabulate(rows, headers=["Ref", "Título", "Estado", "Puntos"],
                       tablefmt="grid"))

    # -- Stories pendientes --
    if metrics["stories_pending"]:
        print()
        print("STORIES PENDIENTES / EN PROGRESO")
        rows = []
        for s in metrics["stories_pending"]:
            ref    = f"#{s.get('ref', '?')}"
            title  = s.get("subject", "")[:55]
            points = s.get("total_points") or "—"
            status = s.get("status_extra_info", {}).get("name", "")
            rows.append([ref, title, status, points])
        print(tabulate(rows, headers=["Ref", "Título", "Estado", "Puntos"],
                       tablefmt="grid"))

    print()
    bar_done = int(metrics["completion"] / 5)
    bar_todo = 20 - bar_done
    print(f"  Progreso: [{'#' * bar_done}{'-' * bar_todo}] {metrics['completion']}%")
    print()


def generate_html_report(metrics: dict, project: dict, output_path: str = "taiga-report.html") -> None:
    """Genera un reporte HTML con todos los datos del proyecto Taiga."""
    now      = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    proj_name = project.get("name", TAIGA_PROJECT)
    proj_url  = f"https://tree.taiga.io/project/{TAIGA_PROJECT}"
    comp      = metrics["completion"]

    stories_rows = ""
    for s in metrics["all_stories"]:
        closed = s.get("is_closed", False)
        status = s.get("status_extra_info", {}).get("name", "—")
        badge  = (f'<span style="color:#16a34a;font-weight:600">✅ {status}</span>'
                  if closed else
                  f'<span style="color:#d97706;font-weight:600">🔄 {status}</span>')
        ref    = s.get("ref", "")
        title  = s.get("subject", "")
        points = s.get("total_points") or "—"
        epic   = (s.get("epic_extra_info") or {}).get("subject", "—")
        stories_rows += f"""
        <tr>
            <td style="color:#64748b">#{ref}</td>
            <td>{title}</td>
            <td>{epic}</td>
            <td style="text-align:center">{points}</td>
            <td>{badge}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GreenCore — Reporte Taiga</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          margin:0; background:#f8fafc; color:#1e293b; }}
  .header {{ background:linear-gradient(135deg,#166534,#15803d);
             color:#fff; padding:2rem 3rem; }}
  .header h1 {{ margin:0; font-size:1.8rem; }}
  .header p  {{ margin:.5rem 0 0; opacity:.85; font-size:.95rem; }}
  .container {{ max-width:1100px; margin:0 auto; padding:2rem 3rem; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
            gap:1rem; margin:2rem 0; }}
  .card {{ background:#fff; border-radius:12px; padding:1.5rem;
           box-shadow:0 1px 4px rgba(0,0,0,.08); text-align:center; }}
  .card .value {{ font-size:2.2rem; font-weight:700; color:#166534; }}
  .card .label {{ font-size:.85rem; color:#64748b; margin-top:.3rem; }}
  .progress-bar {{ background:#e2e8f0; border-radius:99px; height:22px;
                   overflow:hidden; margin:1.5rem 0; }}
  .progress-fill {{ background:linear-gradient(90deg,#16a34a,#22c55e);
                    height:100%; border-radius:99px; display:flex;
                    align-items:center; justify-content:flex-end;
                    padding-right:.75rem; color:#fff; font-weight:700;
                    font-size:.85rem; min-width:2.5rem;
                    transition:width .5s ease;
                    width:{comp}%; }}
  table {{ width:100%; border-collapse:collapse; background:#fff;
           border-radius:12px; overflow:hidden;
           box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  th {{ background:#166534; color:#fff; padding:.85rem 1rem;
        text-align:left; font-size:.88rem; font-weight:600; }}
  td {{ padding:.75rem 1rem; border-bottom:1px solid #f1f5f9;
        font-size:.9rem; }}
  tr:last-child td {{ border-bottom:none; }}
  tr:hover td {{ background:#f0fdf4; }}
  .footer {{ text-align:center; color:#94a3b8; font-size:.82rem;
             padding:2rem; }}
  a {{ color:#16a34a; }}
</style>
</head>
<body>
<div class="header">
  <h1>🌱 GreenCore — Reporte de Trazabilidad Taiga</h1>
  <p>Proyecto: <strong>{proj_name}</strong> &nbsp;|&nbsp;
     <a href="{proj_url}" style="color:#bbf7d0" target="_blank">{proj_url}</a> &nbsp;|&nbsp;
     Generado: {now}</p>
</div>

<div class="container">

  <h2>📊 Resumen del Sprint</h2>
  <div class="cards">
    <div class="card">
      <div class="value">{metrics["total"]}</div>
      <div class="label">Total Stories</div>
    </div>
    <div class="card">
      <div class="value" style="color:#16a34a">{metrics["done"]}</div>
      <div class="label">✅ Completadas</div>
    </div>
    <div class="card">
      <div class="value" style="color:#d97706">{metrics["in_progress"]}</div>
      <div class="label">🔄 En progreso</div>
    </div>
    <div class="card">
      <div class="value" style="color:#64748b">{metrics["pending"] - metrics["in_progress"]}</div>
      <div class="label">📋 Pendientes</div>
    </div>
    <div class="card">
      <div class="value">{metrics["total_points"]}</div>
      <div class="label">Story Points</div>
    </div>
    <div class="card">
      <div class="value">{comp}%</div>
      <div class="label">Completitud</div>
    </div>
  </div>

  <h3>Progreso general</h3>
  <div class="progress-bar">
    <div class="progress-fill">{comp}%</div>
  </div>

  <h2>📋 User Stories</h2>
  <table>
    <thead>
      <tr>
        <th>Ref</th>
        <th>Título</th>
        <th>Epic</th>
        <th style="text-align:center">Puntos</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {stories_rows}
    </tbody>
  </table>

</div>
<div class="footer">
  GreenCore v1.0.0 — Sistema de gestión de invernadero &nbsp;|&nbsp;
  <a href="https://github.com/TROS8/GreenCore" target="_blank">GitHub</a>
</div>
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"✅ Reporte HTML generado: {output_path}")


def generate_csv_report(metrics: dict, output_path: str = "taiga-report.csv") -> None:
    """Genera un reporte CSV con todas las user stories."""
    import csv
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ref", "Titulo", "Epic", "Estado", "Cerrada", "Puntos", "Sprint"])
        for s in metrics["all_stories"]:
            writer.writerow([
                f"#{s.get('ref', '')}",
                s.get("subject", ""),
                (s.get("epic_extra_info") or {}).get("subject", ""),
                s.get("status_extra_info", {}).get("name", ""),
                "Sí" if s.get("is_closed") else "No",
                s.get("total_points") or "",
                (s.get("milestone_extra_info") or {}).get("name", ""),
            ])
    print(f"✅ Reporte CSV generado: {output_path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Modo demo (sin credenciales reales)
# ═══════════════════════════════════════════════════════════════════════════════

DEMO_STORIES = [
    {"ref": 1,  "subject": "Gestión de zonas del invernadero",          "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 1"}},
    {"ref": 2,  "subject": "Registro y autenticación de usuarios",      "is_closed": True,  "total_points": 13, "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Seguridad"}, "milestone_extra_info": {"name": "Sprint 1"}},
    {"ref": 3,  "subject": "OAuth2 con Google",                         "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Seguridad"}, "milestone_extra_info": {"name": "Sprint 1"}},
    {"ref": 4,  "subject": "Gestión de plantas por zona",               "is_closed": True,  "total_points": 5,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 1"}},
    {"ref": 5,  "subject": "Sensores IoT y lecturas en tiempo real",    "is_closed": True,  "total_points": 13, "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 2"}},
    {"ref": 6,  "subject": "Sistema de alertas ambientales",            "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 2"}},
    {"ref": 7,  "subject": "Notificaciones por email (Gmail SMTP)",     "is_closed": True,  "total_points": 5,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Seguridad"}, "milestone_extra_info": {"name": "Sprint 2"}},
    {"ref": 8,  "subject": "Gestión de clientes",                       "is_closed": True,  "total_points": 5,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 2"}},
    {"ref": 9,  "subject": "Registro de ventas con control de stock",   "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Backend"}, "milestone_extra_info": {"name": "Sprint 2"}},
    {"ref": 10, "subject": "Dashboard React con métricas del invernadero","is_closed": True, "total_points": 8, "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Frontend"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 11, "subject": "Internacionalización ES/EN (i18n)",         "is_closed": True,  "total_points": 5,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Frontend"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 12, "subject": "Documentación OpenAPI / Swagger UI",        "is_closed": True,  "total_points": 3,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Docs"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 13, "subject": "Pipeline CI/CD con GitHub Actions",         "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "DevOps"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 14, "subject": "Tests Selenium end-to-end",                 "is_closed": True,  "total_points": 8,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Testing"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 15, "subject": "Generador de código desde modelo.json",     "is_closed": True,  "total_points": 13, "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "DevOps"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 16, "subject": "Conectividad y trazabilidad con Taiga",     "is_closed": True,  "total_points": 5,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "DevOps"}, "milestone_extra_info": {"name": "Sprint 3"}},
    {"ref": 17, "subject": "Deploy automático en servidor de producción","is_closed": False, "total_points": 8,  "status_extra_info": {"name": "In Progress"}, "epic_extra_info": {"subject": "DevOps"}, "milestone_extra_info": {"name": "Sprint 4"}},
    {"ref": 18, "subject": "Modelo ER y diccionario de datos",          "is_closed": True,  "total_points": 3,  "status_extra_info": {"name": "Done"},        "epic_extra_info": {"subject": "Docs"}, "milestone_extra_info": {"name": "Sprint 1"}},
]


def run_demo_mode(report_format: str) -> None:
    """Ejecuta el checker en modo demo con datos de ejemplo."""
    sep = "=" * 70
    print()
    print(sep)
    print("  [DEMO] MODO DEMO -- Credenciales Taiga no configuradas")
    print("  Configure TAIGA_USERNAME y TAIGA_PASSWORD para conectar de verdad.")
    print(sep)

    project = {
        "name":        "GreenCore - Sistema de Invernadero",
        "id":          42,
        "description": "Proyecto de gestión integral de invernadero",
    }

    metrics = analyze_stories(DEMO_STORIES)
    print_console_report(metrics, project)

    if report_format == "html":
        generate_html_report(metrics, project, "taiga-report.html")
    elif report_format == "csv":
        generate_csv_report(metrics, "taiga-report.csv")


# ═══════════════════════════════════════════════════════════════════════════════
# Punto de entrada
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """
    Función principal del checker.

    Returns:
        0 si todas las stories están completadas (o modo sin --ci), 1 en caso contrario.
    """
    parser = argparse.ArgumentParser(
        description="GreenCore — Taiga Connectivity Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--report", choices=["console", "html", "csv"], default="console",
        help="Formato de salida del reporte (default: console)"
    )
    parser.add_argument(
        "--ci", action="store_true",
        help="Modo CI: retorna exit code 1 si el proyecto está por debajo del umbral"
    )
    parser.add_argument(
        "--threshold", type=float, default=70.0,
        help="Porcentaje mínimo de completitud para CI (default: 70)"
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Forzar modo demo aunque haya credenciales"
    )
    args = parser.parse_args()

    # ── Modo demo ──
    if args.demo or not TAIGA_USERNAME or not TAIGA_PASSWORD:
        run_demo_mode(args.report)
        return 0

    # ── Conexión real ──
    client = TaigaClient(API_BASE, TAIGA_USERNAME, TAIGA_PASSWORD)
    if not client.authenticate():
        print("⚠️  Fallando a modo demo por error de autenticación.")
        run_demo_mode(args.report)
        return 0  # No penalizar CI por problemas de auth con Taiga

    project = client.get_project(TAIGA_PROJECT)
    if not project:
        print(f"⚠️  No se encontró el proyecto '{TAIGA_PROJECT}'.")
        print("   Verifica TAIGA_PROJECT en el archivo .env")
        return 1

    print(f"📁 Proyecto: {project['name']} (ID: {project['id']})")

    stories = client.get_user_stories(project["id"])
    print(f"📋 {len(stories)} user stories obtenidas")

    metrics = analyze_stories(stories)
    print_console_report(metrics, project)

    if args.report == "html":
        generate_html_report(metrics, project)
    elif args.report == "csv":
        generate_csv_report(metrics)

    # ── Validación criterios de aceptación ──
    print("🔍 Validando criterios de aceptación...")
    stories_sin_criterios = []
    for story in stories[:10]:  # Limitar para no exceder rate-limit
        detail = client.get_story_detail(story["id"])
        if detail:
            has_criteria, criteria = check_acceptance_criteria(detail)
            if not has_criteria:
                stories_sin_criterios.append(f"#{story['ref']} {story['subject']}")

    if stories_sin_criterios:
        print(f"⚠️  {len(stories_sin_criterios)} stories sin criterios de aceptación:")
        for s in stories_sin_criterios:
            print(f"   • {s}")
    else:
        print("✅ Todas las stories revisadas tienen criterios de aceptación")

    # ── Exit code para CI ──
    if args.ci:
        comp = metrics["completion"]
        if comp < args.threshold:
            print(f"\n❌ CI FAIL: completitud {comp}% < umbral {args.threshold}%")
            return 1
        else:
            print(f"\n✅ CI PASS: completitud {comp}% ≥ umbral {args.threshold}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
