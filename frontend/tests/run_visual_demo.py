"""
GreenCore — Demo Visual de Pruebas Selenium
============================================
Ejecuta las pruebas de Planta CRUD con el navegador VISIBLE para que se
pueda ver en tiempo real cómo Selenium navega, llena formularios y valida datos.

Cómo ejecutar (asegúrate de que el frontend y el backend estén corriendo):

    # Desde la raíz del proyecto:
    python frontend/tests/run_visual_demo.py

    # O con opciones:
    python frontend/tests/run_visual_demo.py --slow          # cada acción tarda 0.8 s
    python frontend/tests/run_visual_demo.py --test crear    # solo el test de crear planta
    python frontend/tests/run_visual_demo.py --no-backend    # omite tests que usen el backend

Requisitos:
    pip install -r frontend/tests/requirements-selenium.txt
    Google Chrome instalado en el sistema

Variables de entorno (opcionales):
    FRONTEND_URL  — por defecto http://localhost:5173
    BACKEND_URL   — por defecto http://localhost:8080
    JWT_SECRET    — por defecto test-jwt-secret-for-junit-only
"""
import sys
import os
import time
import json
import argparse
import requests
from pathlib import Path

# ── Asegurar que conftest.py sea importable ────────────────────────────────────
TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select as SeleniumSelect
from selenium.webdriver.support import expected_conditions as EC

from conftest import (
    BASE_URL, BACKEND_URL, JWT_SECRET, TIMEOUT,
    generate_test_token, go, find, _wait_page_load,
)

# ── Colores ANSI para la terminal ─────────────────────────────────────────────
G  = "\033[92m"   # verde
Y  = "\033[93m"   # amarillo
R  = "\033[91m"   # rojo
B  = "\033[94m"   # azul
W  = "\033[0m"    # reset
BD = "\033[1m"    # negrita

PAUSE = 0.4   # pausa por defecto entre acciones (segundos)


# ── Utilidades ────────────────────────────────────────────────────────────────

def ok(msg):   print(f"  {G}✅ {msg}{W}")
def fail(msg): print(f"  {R}❌ {msg}{W}")
def info(msg): print(f"  {B}ℹ  {msg}{W}")
def step(msg): print(f"\n{BD}{Y}▶ {msg}{W}")


def make_driver(slow=False):
    """Chrome en modo VISIBLE (no headless)."""
    options = Options()
    # SIN --headless → el navegador abre una ventana real
    options.add_argument("--window-size=1400,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    if slow:
        options.add_argument("--auto-open-devtools-for-tabs")  # abre DevTools
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(3)
    return drv


def inject_auth(driver):
    """Inyecta el JWT en localStorage para simular sesión autenticada."""
    driver.get(BASE_URL)
    _wait_page_load(driver)
    token = generate_test_token()
    store_state = {
        "state": {
            "token": token,
            "user": {
                "nombre": "Selenium Tester",
                "email":  "selenium-test@gmail.com",
                "rol":    "ADMIN",
            },
            "role":   "ADMIN",
            "locale": "es",
        },
        "version": 0,
    }
    driver.execute_script(
        "localStorage.setItem('greencore-store', arguments[0]);",
        json.dumps(store_state),
    )
    driver.refresh()
    _wait_page_load(driver)
    time.sleep(0.5)


def api_headers():
    return {
        "Authorization": f"Bearer {generate_test_token()}",
        "Content-Type":  "application/json",
    }


def crear_zona_api():
    """Crea una zona de prueba vía API. Devuelve (zona_id, ok)."""
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/v1/zonas",
            json={
                "nombre": "Zona Demo Visual",
                "descripcion": "Zona creada por el demo visual Selenium",
                "capacidadMaxima": 100,
                "temperaturaMinima": 15,
                "temperaturaMaxima": 30,
                "humedadMinima": 40,
                "humedadMaxima": 80,
                "activa": True,
            },
            headers=api_headers(),
            timeout=8,
        )
        if r.status_code in (200, 201):
            return r.json().get("id"), True
        return None, False
    except Exception as e:
        info(f"Backend no disponible: {e}")
        return None, False


def borrar_zona_api(zona_id):
    if not zona_id:
        return
    try:
        requests.delete(
            f"{BACKEND_URL}/api/v1/zonas/{zona_id}",
            headers=api_headers(), timeout=8
        )
    except Exception:
        pass


def abrir_modal_nueva_planta(driver, pause=PAUSE):
    go(driver, "/plantas")
    time.sleep(pause)
    btn = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(., '+') or contains(., 'Nueva') or contains(., 'Planta') or contains(., 'Crear')]"
        ))
    )
    time.sleep(pause * 0.5)
    btn.click()
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
    )
    time.sleep(pause)


# ══════════════════════════════════════════════════════════════════════════════
# DEMOS INDIVIDUALES
# ══════════════════════════════════════════════════════════════════════════════

def demo_navegacion(driver, pause):
    step("TEST 1 — La página /plantas carga correctamente")
    go(driver, "/plantas")
    time.sleep(pause)
    body = driver.find_element(By.TAG_NAME, "body")
    if "Planta" in body.text or "planta" in body.text:
        ok("Página /plantas cargó con contenido 'Planta'")
    else:
        fail(f"No se encontró 'Planta' en la página. Texto: {body.text[:200]}")

    headings = driver.find_elements(By.TAG_NAME, "h2")
    textos = [h.text for h in headings if h.is_displayed()]
    if any("planta" in t.lower() for t in textos):
        ok(f"Encabezado h2 encontrado: {[t for t in textos if 'planta' in t.lower()]}")
    else:
        info(f"h2 encontrados: {textos}")

    time.sleep(pause)


def demo_modal_campos(driver, pause):
    step("TEST 2 — Modal de nueva planta tiene todos los campos")
    abrir_modal_nueva_planta(driver, pause)

    campos = {
        "nombre":              "input[name='nombre']",
        "especie":             "input[name='especie']",
        "cantidad (number)":   "input[name='cantidad']",
        "precio (number)":     "input[name='precio']",
        "fechaSiembra (date)": "input[name='fechaSiembra']",
        "fechaEstimadaVenta":  "input[name='fechaEstimadaVenta']",
        "estado (select)":     "select[name='estado']",
        "zona (select)":       "select[name='zonaId']",
    }

    for nombre, selector in campos.items():
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            tipo = el.get_attribute("type") or "select"
            ok(f"Campo '{nombre}' presente  [type={tipo}]")
        except Exception:
            fail(f"Campo '{nombre}' NO encontrado con selector '{selector}'")
        time.sleep(pause * 0.3)

    time.sleep(pause)


def demo_validacion_numerica(driver, pause):
    step("TEST 3 — Validación: campos numéricos rechazan texto")

    for campo_name, css in [("cantidad", "input[name='cantidad']"), ("precio", "input[name='precio']")]:
        abrir_modal_nueva_planta(driver, pause)
        campo = driver.find_element(By.CSS_SELECTOR, css)

        info(f"Escribiendo 'abc' en el campo '{campo_name}'...")
        campo.clear()
        campo.send_keys("abc")
        time.sleep(pause)
        valor = campo.get_attribute("value")

        if valor == "" or valor.lstrip("-").replace(".", "").isdigit():
            ok(f"Campo '{campo_name}' rechazó el texto. Valor resultante: '{valor}'")
        else:
            fail(f"Campo '{campo_name}' aceptó texto inválido: '{valor}'")
        time.sleep(pause * 0.5)

        info(f"Escribiendo '999' en el campo '{campo_name}'...")
        campo.clear()
        campo.send_keys("999")
        time.sleep(pause * 0.5)
        valor_num = campo.get_attribute("value")
        if "999" in valor_num:
            ok(f"Campo '{campo_name}' acepta números válidos: '{valor_num}'")
        time.sleep(pause)


def demo_cancelar(driver, pause):
    step("TEST 4 — Cancelar cierra el modal sin crear registros")

    go(driver, "/plantas")
    time.sleep(pause)
    cards_antes = len(driver.find_elements(By.CSS_SELECTOR, ".rounded-2xl.shadow-sm"))
    info(f"Plantas visibles antes: {cards_antes}")

    abrir_modal_nueva_planta(driver, pause)
    nombre_inp = driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
    nombre_inp.send_keys("Planta Que No Se Guardará")
    time.sleep(pause)

    cancelar = driver.find_element(By.XPATH,
        "//button[contains(., 'Cancelar') or contains(., 'Cancel')]")
    info("Haciendo click en 'Cancelar'...")
    cancelar.click()
    time.sleep(pause)

    inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='nombre']")
    if len(inputs) == 0 or not inputs[0].is_displayed():
        ok("Modal cerrado correctamente")
    else:
        fail("El modal NO se cerró")

    cards_despues = len(driver.find_elements(By.CSS_SELECTOR, ".rounded-2xl.shadow-sm"))
    if cards_despues == cards_antes:
        ok(f"Lista sin cambios tras cancelar ({cards_despues} cards)")
    else:
        fail(f"Lista cambió: {cards_antes} → {cards_despues}")
    time.sleep(pause)


def demo_crear_planta(driver, pause):
    step("TEST 5 — Flujo completo: crear planta real desde la UI")

    zona_id, zona_ok = crear_zona_api()
    if not zona_ok:
        info("Backend no disponible — se muestra el flujo visual sin guardar")

    NOMBRE = f"Orquídea Demo {int(time.time()) % 10000}"
    LOTE   = f"LOTE-DEMO-{int(time.time()) % 9999}"

    go(driver, "/plantas")
    time.sleep(1.5)
    abrir_modal_nueva_planta(driver, pause)

    info(f"Llenando formulario con nombre: '{NOMBRE}'")

    for css, val in [
        ("input[name='nombre']",  NOMBRE),
        ("input[name='especie']", "Orchidaceae"),
        ("input[name='lote']",    LOTE),
        ("input[name='cantidad']", "10"),
        ("input[name='precio']",   "45"),
    ]:
        inp = driver.find_element(By.CSS_SELECTOR, css)
        inp.clear()
        inp.send_keys(val)
        time.sleep(pause * 0.4)

    # Fecha via JS
    fecha_inp = driver.find_element(By.CSS_SELECTOR, "input[name='fechaSiembra']")
    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
        "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
        fecha_inp, "2024-03-15"
    )
    time.sleep(pause * 0.5)
    info("Fecha de siembra establecida: 2024-03-15")

    # Zona
    time.sleep(0.8)
    zona_select = driver.find_element(By.CSS_SELECTOR, "select[name='zonaId']")
    sel = SeleniumSelect(zona_select)
    opciones_validas = [o for o in sel.options if o.get_attribute("value")]
    if opciones_validas:
        sel.select_by_value(opciones_validas[0].get_attribute("value"))
        ok(f"Zona seleccionada: {opciones_validas[0].text.strip()}")
    else:
        info("No hay zonas en el dropdown (backend vacío o no disponible)")
    time.sleep(pause)

    # Guardar
    guardar = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(., 'Guardar') or contains(., 'Save')]"
        ))
    )
    info("Haciendo click en 'Guardar'...")
    guardar.click()

    try:
        WebDriverWait(driver, TIMEOUT + 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
        )
        time.sleep(1.5)
        body = driver.find_element(By.TAG_NAME, "body").text
        if NOMBRE in body:
            ok(f"¡Planta '{NOMBRE}' creada y visible en la lista!")
        else:
            info(f"Modal cerrado. Verificar lista manualmente (texto visible: {body[:300]})")
    except Exception as e:
        body = driver.find_element(By.TAG_NAME, "body").text
        fail(f"El modal no se cerró: {e}")
        info(f"Estado de la página: {body[:400]}")

    borrar_zona_api(zona_id)
    time.sleep(pause)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Demo visual de las pruebas Selenium de GreenCore — Plantas CRUD"
    )
    parser.add_argument(
        "--slow", action="store_true",
        help="Añade pausas más largas entre acciones (0.8 s)"
    )
    parser.add_argument(
        "--test",
        choices=["nav", "campos", "validacion", "cancelar", "crear", "all"],
        default="all",
        help="Demo a ejecutar (por defecto: all)"
    )
    args = parser.parse_args()

    pause = 0.8 if args.slow else PAUSE

    print()
    print(f"{BD}{'=' * 62}{W}")
    print(f"{BD}   GreenCore — Demo Visual Selenium (Chrome visible){W}")
    print(f"{BD}{'=' * 62}{W}")
    print(f"  Frontend : {BASE_URL}")
    print(f"  Backend  : {BACKEND_URL}")
    print(f"  Pausa    : {pause}s entre acciones")
    print(f"  Demo     : {args.test}")
    print(f"{BD}{'=' * 62}{W}")
    print()

    driver = make_driver(slow=args.slow)
    try:
        # ── Autenticación ──────────────────────────────────────────────────────
        step("Autenticando usuario de prueba (Selenium Tester / ADMIN)")
        inject_auth(driver)
        ok("JWT inyectado en localStorage — sesión activa")
        time.sleep(pause)

        # ── Ejecutar demos seleccionados ───────────────────────────────────────
        run_all  = args.test == "all"
        if run_all or args.test == "nav":       demo_navegacion(driver, pause)
        if run_all or args.test == "campos":    demo_modal_campos(driver, pause)
        if run_all or args.test == "validacion":demo_validacion_numerica(driver, pause)
        if run_all or args.test == "cancelar":  demo_cancelar(driver, pause)
        if run_all or args.test == "crear":     demo_crear_planta(driver, pause)

        # ── Resultado final ────────────────────────────────────────────────────
        print()
        print(f"{BD}{G}{'=' * 62}{W}")
        print(f"{BD}{G}   ✅ Demo completado — el navegador permanece abierto 5 s{W}")
        print(f"{BD}{G}{'=' * 62}{W}")
        print()
        time.sleep(5)  # dejar que el profesor vea la pantalla final

    except KeyboardInterrupt:
        print(f"\n{Y}Demo interrumpido por el usuario.{W}")
    except Exception as e:
        print(f"\n{R}Error inesperado en el demo: {e}{W}")
        import traceback; traceback.print_exc()
        time.sleep(3)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
