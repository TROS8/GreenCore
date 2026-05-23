"""
Pruebas de la barra de navegacion: enlaces, cambio de idioma, estado activo.
"""
import pytest
from selenium.webdriver.common.by import By
from conftest import BASE_URL, go, find, find_all, click, text_present


RUTAS_NAV = [
    ("/zonas",    ["zona", "Zona", "Zone"]),
    ("/plantas",  ["planta", "Planta", "Plant"]),
    ("/sensores", ["sensor", "Sensor"]),
    ("/alertas",  ["alerta", "Alerta", "Alert"]),
    ("/clientes", ["cliente", "Cliente", "Client"]),
    ("/ventas",   ["venta", "Venta", "Sale"]),
    ("/usuarios", ["usuario", "Usuario", "User"]),
]


class TestNavbar:
    """Verifica estructura y comportamiento de la barra de navegacion."""

    def test_logo_greencore_presente(self, auth_driver):
        go(auth_driver, "/")
        nav = find(auth_driver, "nav")
        assert "GreenCore" in nav.text

    def test_todos_los_enlaces_presentes(self, auth_driver):
        go(auth_driver, "/")
        nav = find(auth_driver, "nav")
        nav_text = nav.text.lower()
        for keyword in ["zona", "planta", "sensor", "alert", "cliente", "venta", "usuario"]:
            assert keyword in nav_text, f"Enlace '{keyword}' no encontrado en navbar"

    def test_enlace_activo_resaltado(self, auth_driver):
        go(auth_driver, "/zonas")
        active_links = auth_driver.find_elements(
            By.CSS_SELECTOR, "nav a.bg-emerald-900"
        )
        assert len(active_links) >= 1, "Debe haber al menos un enlace activo resaltado"

    def test_navegacion_a_todas_las_rutas(self, auth_driver):
        for ruta, palabras_clave in RUTAS_NAV:
            go(auth_driver, ruta)
            body = find(auth_driver, "body")
            assert any(p in body.text for p in palabras_clave), \
                f"Pagina {ruta} debe contener alguna de: {palabras_clave}"

    def test_boton_cambio_idioma_presente(self, auth_driver):
        go(auth_driver, "/")
        nav = find(auth_driver, "nav")
        assert "EN" in nav.text or "ES" in nav.text


class TestCambioIdioma:
    """Verifica el toggle de internacionalizacion en la navbar."""

    def test_toggle_cambia_texto_a_ingles(self, auth_driver):
        go(auth_driver, "/zonas")
        nav = find(auth_driver, "nav")

        # Boton que muestra "EN" cuando el idioma actual es "es"
        lang_btn = auth_driver.find_element(
            By.XPATH, "//button[normalize-space()='EN' or normalize-space()='ES']"
        )
        idioma_inicial = lang_btn.text.strip()
        lang_btn.click()

        import time; time.sleep(0.5)
        nav_after = find(auth_driver, "nav")
        idioma_nuevo = auth_driver.find_element(
            By.XPATH, "//button[normalize-space()='EN' or normalize-space()='ES']"
        ).text.strip()

        assert idioma_nuevo != idioma_inicial, "El boton de idioma debe cambiar al hacer click"

    def test_toggle_vuelve_al_idioma_original(self, auth_driver):
        go(auth_driver, "/")
        lang_btn = auth_driver.find_element(
            By.XPATH, "//button[normalize-space()='EN' or normalize-space()='ES']"
        )
        idioma_inicial = lang_btn.text.strip()

        lang_btn.click()
        import time; time.sleep(0.3)
        lang_btn = auth_driver.find_element(
            By.XPATH, "//button[normalize-space()='EN' or normalize-space()='ES']"
        )
        lang_btn.click()
        import time; time.sleep(0.3)

        lang_btn_final = auth_driver.find_element(
            By.XPATH, "//button[normalize-space()='EN' or normalize-space()='ES']"
        )
        assert lang_btn_final.text.strip() == idioma_inicial, "Segundo toggle debe restaurar idioma original"
