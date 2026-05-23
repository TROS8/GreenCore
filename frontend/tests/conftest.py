"""
Configuracion global de pruebas Selenium para GreenCore Frontend.
Genera un JWT de prueba, lo inyecta en localStorage (Zustand persist)
y expone fixtures reutilizables para todos los tests.
"""
import json
import time
import pytest
import jwt as pyjwt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ── Constantes ────────────────────────────────────────────────────────────────
BASE_URL    = "http://localhost:5173"
JWT_SECRET  = "test-jwt-secret-for-junit-only"  # mismo que application-test.properties
TEST_EMAIL  = "selenium-test@gmail.com"
TEST_NAME   = "Selenium Tester"
TEST_ROLE   = "ADMIN"
TIMEOUT     = 10  # segundos de espera maxima


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

    drv = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


# ── Fixture: driver CON autenticacion ─────────────────────────────────────────
@pytest.fixture(scope="function")
def auth_driver(driver):
    """
    WebDriver con token JWT inyectado en localStorage (formato Zustand persist).
    Navega a BASE_URL primero para que localStorage este disponible, luego inyecta
    el token y recarga — el store de Zustand lo levanta automaticamente.
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
            "locale": "es",
            "sessionExpired": False,
        },
        "version": 0,
    }
    driver.execute_script(
        "localStorage.setItem('greencore-store', arguments[0]);",
        json.dumps(store_state),
    )
    driver.refresh()
    _wait_page_load(driver)
    return driver


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
    """Espera a que el DOM este listo."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


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
