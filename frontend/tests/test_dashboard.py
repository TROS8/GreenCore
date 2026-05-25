"""
Pruebas del Dashboard: carga, tarjetas de resumen, graficos y navegacion rapida.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import go, find, TIMEOUT


class TestDashboard:
    """Verifica el dashboard principal del sistema."""

    def test_dashboard_carga(self, auth_driver):
        go(auth_driver, "/")
        body = find(auth_driver, "body")
        # No debe mostrar pantalla de login
        assert "Debes iniciar sesión" not in body.text

    def test_navbar_visible_en_dashboard(self, auth_driver):
        go(auth_driver, "/")
        nav = find(auth_driver, "nav")
        assert nav.is_displayed()
        assert "GreenCore" in nav.text

    def test_dashboard_contiene_estadisticas_o_bienvenida(self, auth_driver):
        go(auth_driver, "/")
        time.sleep(1.5)
        body = auth_driver.find_element(By.TAG_NAME, "body")
        keywords = ["zona", "planta", "sensor", "alerta", "venta", "dashboard", "GreenCore", "invernadero"]
        texto_lower = body.text.lower()
        assert any(k.lower() in texto_lower for k in keywords), \
            f"Dashboard debe mostrar contenido relevante. Texto: {body.text[:400]}"

    def test_enlaces_rapidos_o_cards_presentes(self, auth_driver):
        go(auth_driver, "/")
        time.sleep(1.5)
        # Busca tarjetas de estadisticas o elementos de contenido
        # Acepta clases de Tailwind v2/v3: rounded, rounded-lg, rounded-2xl,
        # shadow, shadow-sm, shadow-md, bg-white, p-4, p-5, p-6
        cards = auth_driver.find_elements(By.CSS_SELECTOR,
            "div.rounded, div.rounded-lg, div.rounded-2xl, "
            "div.shadow, div.shadow-sm, div.shadow-md, "
            "div.bg-white, div.p-4, div.p-5, div.p-6")
        assert len(cards) > 0, "El dashboard debe tener al menos un elemento de contenido"

    def test_url_es_raiz(self, auth_driver):
        go(auth_driver, "/")
        assert auth_driver.current_url.rstrip("/") == "http://localhost:5173" or \
               auth_driver.current_url == "http://localhost:5173/"

    def test_titulo_en_pestana(self, auth_driver):
        go(auth_driver, "/")
        title = auth_driver.title
        assert title != "", "La pagina debe tener un titulo en la pestana del navegador"
