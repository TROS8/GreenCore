"""
GreenCore — Demo del reporter automático de fallos en Taiga
===========================================================
Simula exactamente lo que hace conftest.py cuando un test Selenium falla.
Ejecutar con:  python taiga-client/demo_reporter.py

Crea una User Story REAL en el proyecto Taiga con los datos de un fallo
de ejemplo, para verificar que la integración funciona correctamente.
"""
import sys
import os
from pathlib import Path

# Asegurar que taiga_reporter.py sea localizable
sys.path.insert(0, str(Path(__file__).parent))
from taiga_reporter import get_reporter

# ── Datos de ejemplo que simula un fallo de Selenium ──────────────────────────
FAKE_FAILURE = {
    "test_nodeid": "frontend/tests/test_plantas_crud.py::TestValidacionCampos::test_texto_en_campo_cantidad_no_se_acepta",
    "error_message": (
        "AssertionError: Campo numérico 'cantidad' no debe aceptar texto. Valor obtenido: 'abc'\n"
        "assert 'abc' == '' or 'abc'.lstrip('-').replace('.','').isdigit()\n"
        "  - El input type=number debería rechazar texto pero el valor fue 'abc'\n"
        "  - URL: http://localhost:5173/plantas\n"
        "  - Screenshot guardado en: /tmp/screenshots/test_texto_en_campo_cantidad.png"
    ),
    "screenshot_path": "/tmp/screenshots/test_texto_en_campo_cantidad.png",
}

def main():
    print("=" * 60)
    print("  GreenCore — Demo: Taiga Auto-Reporter")
    print("=" * 60)
    print()
    print("Simulando un fallo de prueba Selenium...")
    print(f"  Test:  {FAKE_FAILURE['test_nodeid'].split('::')[-1]}")
    print(f"  Error: {FAKE_FAILURE['error_message'].splitlines()[0]}")
    print()

    reporter = get_reporter()

    if not reporter.enabled:
        print("❌ Credenciales no configuradas.")
        print("   Asegúrate de tener TAIGA_USERNAME, TAIGA_PASSWORD y TAIGA_PROJECT en:")
        print("   taiga-client/.env")
        sys.exit(1)

    print("✅ Credenciales encontradas. Conectando con Taiga...")
    print()

    resultado = reporter.report_failure(
        test_nodeid=FAKE_FAILURE["test_nodeid"],
        error_message=FAKE_FAILURE["error_message"],
        screenshot_path=FAKE_FAILURE["screenshot_path"],
    )

    print()
    print("=" * 60)
    if resultado:
        print("✅ ¡ÉXITO! Ve a tu proyecto Taiga y busca la historia:")
        print("   [TEST FALLIDO] test_texto_en_campo_cantidad_no_se_acepta")
        print()
        print("   URL del proyecto:")
        print("   https://tree.taiga.io/project/tros8-greencore/backlog")
    else:
        print("❌ No se pudo crear el issue. Revisa las credenciales o la conexión.")
    print("=" * 60)

if __name__ == "__main__":
    main()
