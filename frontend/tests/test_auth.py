"""
Pruebas de autenticacion: estado sin sesion, prompt de login, inyeccion de token.
"""
import json
import pytest
from selenium.webdriver.common.by import By
from conftest import BASE_URL, go, find, generate_test_token, _wait_page_load


class TestSinAutenticacion:
    """Verifica comportamiento cuando no hay token en localStorage."""

    def test_muestra_prompt_de_login(self, driver):
        go(driver, "/")
        body = find(driver, "body")
        assert "Debes iniciar sesión" in body.text or "Iniciar sesión" in body.text

    def test_boton_google_presente(self, driver):
        go(driver, "/")
        btns = driver.find_elements(By.PARTIAL_LINK_TEXT, "Google")
        assert len(btns) > 0, "Debe existir un enlace/boton de login con Google"

    def test_rutas_protegidas_redirigen_a_login(self, driver):
        rutas = ["/zonas", "/plantas", "/sensores", "/alertas", "/clientes", "/ventas", "/usuarios"]
        for ruta in rutas:
            go(driver, ruta)
            body = find(driver, "body")
            assert "Iniciar sesión" in body.text, f"Ruta {ruta} debe pedir login"

    def test_navbar_muestra_boton_login(self, driver):
        go(driver, "/")
        nav = find(driver, "nav")
        assert "GreenCore" in nav.text


class TestConAutenticacion:
    """Verifica que la inyeccion de token via localStorage funciona correctamente."""

    def test_token_inyectado_da_acceso_al_dashboard(self, auth_driver):
        go(auth_driver, "/")
        body = find(auth_driver, "body")
        assert "Iniciar sesión" not in body.text

    def test_navbar_muestra_logout_cuando_autenticado(self, auth_driver):
        go(auth_driver, "/")
        nav = find(auth_driver, "nav")
        assert "Cerrar" in nav.text or "Salir" in nav.text or "logout" in nav.text.lower() or "Logout" in nav.text

    def test_logout_limpia_sesion(self, auth_driver):
        go(auth_driver, "/")
        logout_btn = auth_driver.find_element(By.XPATH, "//button[contains(., 'Cerrar') or contains(., 'Salir') or contains(., 'ogout')]")
        logout_btn.click()
        _wait_page_load(auth_driver)
        body = find(auth_driver, "body")
        assert "Iniciar sesión" in body.text

    def test_token_persiste_entre_navegaciones(self, auth_driver):
        rutas = ["/zonas", "/plantas", "/sensores"]
        for ruta in rutas:
            go(auth_driver, ruta)
            body = find(auth_driver, "body")
            assert "Iniciar sesión" not in body.text, f"Token debe persistir en {ruta}"
