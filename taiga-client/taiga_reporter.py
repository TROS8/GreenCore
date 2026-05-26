"""
GreenCore — Taiga Automatic Test Failure Reporter
=================================================
Crea una User Story en Taiga automáticamente cuando una prueba Selenium falla.

Diseñado para ser llamado desde conftest.py en el hook pytest_runtest_makereport.
Si las credenciales no están configuradas, opera en modo silencioso (no hace nada).

Variables de entorno requeridas (o en taiga-client/.env):
    TAIGA_USERNAME  → usuario de Taiga
    TAIGA_PASSWORD  → contraseña de Taiga
    TAIGA_PROJECT   → slug del proyecto (ej: tros8-greencore)
    TAIGA_URL       → base URL (default: https://api.taiga.io)

Uso desde conftest.py:
    from taiga_reporter import get_reporter
    reporter = get_reporter()
    if reporter.enabled:
        reporter.report_failure(test_nodeid, error_message)
"""

import os
import sys
import datetime
import requests
from pathlib import Path

# ── Cargar .env desde el directorio de este módulo ──────────────────────────
try:
    from dotenv import load_dotenv
    # Intentar desde el directorio del módulo
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=False)
    else:
        load_dotenv(override=False)  # buscar en directorio actual
except ImportError:
    pass  # python-dotenv no instalado, se usan solo las variables de entorno

TAIGA_URL = os.getenv("TAIGA_URL", "https://api.taiga.io").rstrip("/")
USERNAME  = os.getenv("TAIGA_USERNAME", "")
PASSWORD  = os.getenv("TAIGA_PASSWORD", "")
SLUG      = os.getenv("TAIGA_PROJECT",  "tros8-greencore")

API_BASE  = f"{TAIGA_URL}/api/v1"
TIMEOUT   = 12  # segundos para cada petición HTTP


class TaigaReporter:
    """
    Reporta fallos de pruebas Selenium como User Stories en Taiga.

    Cada fallo genera una historia con:
    - Título: [TEST FALLIDO] <nombre del test>
    - Descripción: detalles del error, traceback, timestamp
    - Estado: primero disponible en el proyecto (típicamente 'New')
    - Deduplicación: no crea duplicados si ya existe una historia con el mismo título
    """

    def __init__(self):
        self._token      = None
        self._project_id = None
        self._status_id  = None
        self._enabled    = bool(USERNAME and PASSWORD and SLUG)

    @property
    def enabled(self) -> bool:
        """True si las credenciales están configuradas."""
        return self._enabled

    # ── Autenticación ─────────────────────────────────────────────────────────
    def _authenticate(self) -> bool:
        if self._token:
            return True
        try:
            resp = requests.post(
                f"{API_BASE}/auth",
                json={"type": "normal", "username": USERNAME, "password": PASSWORD},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                self._token = resp.json()["auth_token"]
                return True
            print(f"[Taiga] Auth HTTP {resp.status_code}: {resp.text[:120]}")
        except Exception as exc:
            print(f"[Taiga] Auth error: {exc}")
        return False

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type":  "application/json",
        }

    # ── Proyecto ──────────────────────────────────────────────────────────────
    def _load_project(self) -> bool:
        if self._project_id:
            return True
        try:
            resp = requests.get(
                f"{API_BASE}/projects/by_slug",
                params={"slug": SLUG},
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                print(f"[Taiga] Project '{SLUG}' not found (HTTP {resp.status_code})")
                return False

            self._project_id = resp.json()["id"]

            # Obtener primer estado disponible ("New")
            sr = requests.get(
                f"{API_BASE}/userstory-statuses",
                params={"project": self._project_id},
                headers=self._headers(),
                timeout=TIMEOUT,
            )
            if sr.status_code == 200 and sr.json():
                self._status_id = sr.json()[0]["id"]
            return True
        except Exception as exc:
            print(f"[Taiga] Project load error: {exc}")
        return False

    # ── Deduplicación ─────────────────────────────────────────────────────────
    def _story_exists(self, subject: str) -> bool:
        """Devuelve True si ya hay una historia con ese título exacto."""
        page = 1
        try:
            while True:
                resp = requests.get(
                    f"{API_BASE}/userstories",
                    params={"project": self._project_id, "page": page, "page_size": 100},
                    headers=self._headers(),
                    timeout=TIMEOUT,
                )
                if resp.status_code != 200:
                    break
                stories = resp.json()
                for s in stories:
                    if s.get("subject", "").strip() == subject.strip():
                        return True
                if len(stories) < 100:
                    break
                page += 1
        except Exception:
            pass
        return False

    # ── Reporte principal ─────────────────────────────────────────────────────
    def report_failure(
        self,
        test_nodeid:   str,
        error_message: str = "",
        screenshot_path: str = "",
    ) -> bool:
        """
        Crea una User Story en Taiga para un test fallido.

        Parámetros:
            test_nodeid     ID completo del test (ej: test_plantas.py::TestCRUD::test_crear)
            error_message   Mensaje del error / assertion
            screenshot_path Ruta al screenshot del fallo (solo referencia, no se adjunta)

        Devuelve True si la historia fue creada o ya existía, False si hubo error.
        """
        if not self._enabled:
            return False

        try:
            if not self._authenticate():
                return False
            if not self._load_project():
                return False

            # Nombre limpio del test
            test_name = test_nodeid.replace("/", ".").replace("\\", ".")
            short_name = test_nodeid.split("::")[-1] if "::" in test_nodeid else test_nodeid
            subject = f"[TEST FALLIDO] {short_name}"

            print(f"\n[Taiga] Verificando duplicado: '{subject}'")
            if self._story_exists(subject):
                print(f"[Taiga]   Ya existe, se omite la creación.")
                return True

            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            description = self._build_description(
                test_name, error_message, timestamp, screenshot_path
            )

            payload = {
                "project":     self._project_id,
                "subject":     subject,
                "status":      self._status_id,
                "description": description,
                "tags":        [["selenium", "#e63946"], ["auto-report", "#2a9d8f"]],
            }
            resp = requests.post(
                f"{API_BASE}/userstories",
                headers=self._headers(),
                json=payload,
                timeout=TIMEOUT,
            )
            if resp.status_code == 201:
                ref = resp.json().get("ref", "?")
                print(f"[Taiga] ✅ Historia creada: #{ref} — {subject}")
                return True
            print(f"[Taiga] ❌ HTTP {resp.status_code}: {resp.text[:200]}")

        except Exception as exc:
            print(f"[Taiga] Excepción al reportar: {exc}")

        return False

    # ── Construcción de descripción ───────────────────────────────────────────
    @staticmethod
    def _build_description(
        test_name: str,
        error_message: str,
        timestamp: str,
        screenshot_path: str,
    ) -> str:
        lines = [
            "## 🤖 Fallo detectado automáticamente por Selenium",
            "",
            f"| Campo | Valor |",
            f"|---|---|",
            f"| **Test** | `{test_name}` |",
            f"| **Fecha** | {timestamp} |",
            f"| **Entorno** | CI / GitHub Actions |",
        ]
        if screenshot_path:
            lines.append(f"| **Screenshot** | `{screenshot_path}` |")

        if error_message:
            # Truncar para no saturar Taiga
            msg = error_message[:900] + ("…" if len(error_message) > 900 else "")
            lines += [
                "",
                "### Error",
                "```",
                msg,
                "```",
            ]

        lines += [
            "",
            "### Criterios de corrección",
            "- [ ] Reproducir el fallo localmente",
            "- [ ] Identificar la causa raíz",
            "- [ ] Corregir el bug o actualizar la prueba",
            "- [ ] Verificar que la prueba pasa en CI",
            "- [ ] Cerrar esta historia",
        ]
        return "\n".join(lines)


# ── Singleton ─────────────────────────────────────────────────────────────────
_reporter: TaigaReporter | None = None


def get_reporter() -> TaigaReporter:
    """Devuelve la instancia singleton del reporter."""
    global _reporter
    if _reporter is None:
        _reporter = TaigaReporter()
    return _reporter
