"""
Configuracion global de pruebas Selenium para GreenCore Frontend.
Genera un JWT de prueba, lo inyecta en localStorage (Zustand persist)
y expone fixtures reutilizables para todos los tests.

Integración con Taiga:
    Cuando una prueba falla se crea automáticamente una User Story en Taiga
    con el detalle del error. Requiere las variables de entorno:
        TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_PROJECT
    Si no están configuradas, el fallo se ignora silenciosamente.
"""
import json
import time
import os
import sys
import pytest
import jwt as pyjwt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ── Constantes ────────────────────────────────────────────────────────────────
BASE_URL    = os.environ.get("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.environ.get("BACKEND_URL",  "http://localhost:8080")
JWT_SECRET  = os.environ.get("JWT_SECRET",   "test-jwt-secret-for-junit-only")
TEST_EMAIL  = "selenium-test@gmail.com"
TEST_NAME   = "Selenium Tester"
TEST_ROLE   = "ADMIN"
TIMEOUT     = 15  # segundos de espera maxima


# ── Taiga reporter (opcional) ─────────────────────────────────────────────────
# Se busca taiga_reporter en taiga-client/ (../../taiga-client relativo a este archivo)
_TAIGA_REPORTER_AVAILABLE = False
try:
    _taiga_client_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "taiga-client")
    )
    if _taiga_client_path not in sys.path:
        sys.path.insert(0, _taiga_client_path)
    from taiga_reporter import get_reporter as _get_taiga_reporter
    _TAIGA_REPORTER_AVAILABLE = True
    print("[conftest] Taiga reporter cargado correctamente.")
except ImportError:
    print("[conftest] Taiga reporter no disponible (se continua sin el).")


# ── Generador de token ────────────────────────────────────────────────────────
def generate_test_token(email=TEST_EMAIL, role=TEST_ROLE, secret=JWT_SECRET):
    """Genera un JWT firmado con el mismo secreto que usa el backend en tests."""
    now = int(time.time())
    payload = {
        "sub":  email,
        "role": role,
        "iat":  now,
        "exp":  now + 86400,  # 24 horas
    }
    return pyjwt.encode(payload, secret, algorithm="HS256")


# ── Fixture: driver sin autenticacion ─────────────────────────────────────────
@pytest.fixture(scope="function")
def driver():
    """WebDriver Chrome headless sin token inyectado."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # Selenium Manager (incluido en selenium>=4.6) descarga chromedriver automaticamente
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


# ── Fixture: driver CON autenticacion ─────────────────────────────────────────
@pytest.fixture(scope="function")
def auth_driver(driver):
    """
    WebDriver con token JWT inyectado en localStorage (formato Zustand persist).
    Navega a BASE_URL primero para que localStorage este disponible, luego inyecta
    el token y recarga — el store de Zustand lo levanta automaticamente.
    Espera a que el estado autenticado sea confirmado antes de retornar.
    """
    driver.get(BASE_URL)
    _wait_page_load(driver)

    token = generate_test_token()
    store_state = {
        "state": {
            "token": token,
            "user": {
                "nombre": TEST_NAME,
                "email":  TEST_EMAIL,
                "rol":    TEST_ROLE,
            },
            "role":   TEST_ROLE,
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

    # Dar tiempo adicional a Zustand para hidratar de forma asincrona
    time.sleep(0.5)

    # Verificar que el estado autenticado este activo leyendo el store
    try:
        stored = driver.execute_script(
            "return localStorage.getItem('greencore-store');"
        )
        print(f"\n[auth_driver] localStorage after refresh: {stored[:200] if stored else 'EMPTY'}")
    except Exception as e:
        print(f"\n[auth_driver] Error reading localStorage: {e}")

    # Esperar a que el boton de logout aparezca (confirma estado autenticado)
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(., 'Cerrar') or contains(., 'Salir') or contains(., 'ogout')]")
            )
        )
        print("\n[auth_driver] ✅ Authenticated state confirmed (logout button visible)")
    except Exception as e:
        body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
        print(f"\n[auth_driver] ⚠️  Logout button not found: {e}")
        print(f"[auth_driver] Body text: {body_text}")

    return driver


# ── Hook: screenshot + reporte Taiga en fallo ─────────────────────────────────
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Al fallar un test:
      1. Captura screenshot y guarda en /tmp/screenshots/
      2. Imprime el texto del body para depuracion
      3. Crea automáticamente una User Story en Taiga con los detalles del fallo
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # ── 1. Obtener driver ────────────────────────────────────────────────
        drv = None
        for fixture_name in ("auth_driver", "driver"):
            drv = item.funcargs.get(fixture_name)
            if drv:
                break

        screenshot_path = ""

        # ── 2. Screenshot ────────────────────────────────────────────────────
        if drv:
            screenshots_dir = "/tmp/screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            safe_name = rep.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
            screenshot_path = f"{screenshots_dir}/{safe_name}.png"
            try:
                drv.save_screenshot(screenshot_path)
                print(f"\n[screenshot] Saved to {screenshot_path}")
                body = drv.find_element(By.TAG_NAME, "body")
                print(f"[body_text] {body.text[:800]}")
            except Exception as exc:
                print(f"\n[screenshot] Failed to save: {exc}")
                screenshot_path = ""

        # ── 3. Reporte automático en Taiga ───────────────────────────────────
        if _TAIGA_REPORTER_AVAILABLE:
            try:
                reporter = _get_taiga_reporter()
                if reporter.enabled:
                    error_msg = str(rep.longrepr) if rep.longrepr else "Error desconocido"
                    reporter.report_failure(
                        test_nodeid=rep.nodeid,
                        error_message=error_msg,
                        screenshot_path=screenshot_path,
                    )
                else:
                    print("\n[Taiga] Credenciales no configuradas — se omite el reporte.")
            except Exception as exc:
                # Nunca debe interrumpir el flujo de pytest
                print(f"\n[Taiga] Error al reportar fallo (no critico): {exc}")


# ── Fixture: wait helper ───────────────────────────────────────────────────────
@pytest.fixture(scope="function")
def wait(auth_driver):
    """WebDriverWait ligado al auth_driver."""
    return WebDriverWait(auth_driver, TIMEOUT)


# ── Helpers publicos ───────────────────────────────────────────────────────────
def go(driver, path="/"):
    """Navega a una ruta del frontend y espera carga."""
    driver.get(f"{BASE_URL}{path}")
    _wait_page_load(driver)


def _wait_page_load(driver, timeout=TIMEOUT):
    """Espera a que el DOM este listo y React haya renderizado."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    # Pequeno buffer para que React complete el render inicial
    time.sleep(0.2)


def find(driver, css, timeout=TIMEOUT):
    """Espera y retorna el primer elemento que coincide con el selector CSS."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css))
    )


def find_all(driver, css):
    """Retorna todos los elementos que coinciden con el selector CSS (sin espera)."""
    return driver.find_elements(By.CSS_SELECTOR, css)


def click(driver, css, timeout=TIMEOUT):
    """Espera que el elemento sea clickeable y hace click."""
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, css))
    )
    el.click()
    return el


def text_present(driver, text, timeout=TIMEOUT):
    """Retorna True si el texto aparece en el body de la pagina."""
    return WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text)
    )
