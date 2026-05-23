"""
Pruebas smoke de todas las vistas del sistema.
Verifica que cada pagina carga, muestra su titulo y el boton de accion principal
(cuando aplica). No depende de datos en el backend.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import go, find, TIMEOUT


# Definicion de cada vista: (ruta, keywords_titulo, tiene_boton_crear)
VISTAS = [
    ("/zonas",    ["Zona", "zona"],    True),
    ("/plantas",  ["Planta", "planta"], True),
    ("/sensores", ["Sensor", "sensor"], True),
    ("/alertas",  ["Alerta", "alerta"], False),
    ("/clientes", ["Cliente", "cliente"], True),
    ("/ventas",   ["Venta", "venta"],   False),
    ("/usuarios", ["Usuario", "usuario"], False),
]


class TestCargaDePaginas:
    """Verifica que todas las rutas cargan sin error."""

    @pytest.mark.parametrize("ruta,keywords,_", VISTAS)
    def test_pagina_carga_sin_error(self, auth_driver, ruta, keywords, _):
        go(auth_driver, ruta)
        time.sleep(0.8)
        body = find(auth_driver, "body")
        assert any(k in body.text for k in keywords), \
            f"Pagina {ruta} debe contener alguno de {keywords}. Texto: {body.text[:300]}"

    @pytest.mark.parametrize("ruta,_,tiene_boton", VISTAS)
    def test_boton_crear_cuando_aplica(self, auth_driver, ruta, _, tiene_boton):
        if not tiene_boton:
            pytest.skip(f"{ruta} no tiene boton de crear")
        go(auth_driver, ruta)
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nuevo') or contains(., 'Nueva') or contains(., 'Crear')]"))
        )
        assert btn.is_displayed(), f"Boton de crear debe estar visible en {ruta}"


class TestPlantaVista:
    """Verifica elementos especificos de la vista Plantas."""

    def test_titulo_plantas(self, auth_driver):
        go(auth_driver, "/plantas")
        body = find(auth_driver, "body")
        assert "Planta" in body.text or "planta" in body.text

    def test_boton_nueva_planta(self, auth_driver):
        go(auth_driver, "/plantas")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nueva') or contains(., 'Crear')]"))
        )
        assert btn.is_displayed()

    def test_modal_planta_tiene_campos_clave(self, auth_driver):
        go(auth_driver, "/plantas")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nueva') or contains(., 'Crear')]"))
        )
        btn.click()
        time.sleep(0.5)
        campos = ["nombre", "especie", "cantidad", "precio"]
        for campo in campos:
            els = auth_driver.find_elements(By.CSS_SELECTOR, f"input[name='{campo}']")
            assert len(els) > 0, f"Campo '{campo}' debe aparecer en modal de planta"


class TestSensorVista:
    """Verifica elementos especificos de la vista Sensores."""

    def test_titulo_sensores(self, auth_driver):
        go(auth_driver, "/sensores")
        body = find(auth_driver, "body")
        assert "Sensor" in body.text or "sensor" in body.text

    def test_modal_sensor_tiene_campos_clave(self, auth_driver):
        go(auth_driver, "/sensores")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nuevo') or contains(., 'Crear')]"))
        )
        btn.click()
        time.sleep(0.5)
        campos = ["codigo", "unidad", "umbralMinimo", "umbralMaximo"]
        for campo in campos:
            els = auth_driver.find_elements(By.CSS_SELECTOR, f"input[name='{campo}']")
            assert len(els) > 0, f"Campo '{campo}' debe aparecer en modal de sensor"


class TestAlertaVista:
    """Verifica la vista de Alertas."""

    def test_titulo_alertas(self, auth_driver):
        go(auth_driver, "/alertas")
        body = find(auth_driver, "body")
        assert "Alerta" in body.text or "alerta" in body.text

    def test_no_hay_boton_crear(self, auth_driver):
        go(auth_driver, "/alertas")
        time.sleep(0.5)
        btns_crear = auth_driver.find_elements(By.XPATH,
            "//button[contains(., 'Nueva Alerta') or contains(., 'Crear Alerta')]")
        assert len(btns_crear) == 0, "Alertas se generan automaticamente, no manualmente"


class TestClienteVista:
    """Verifica elementos de la vista Clientes."""

    def test_titulo_clientes(self, auth_driver):
        go(auth_driver, "/clientes")
        body = find(auth_driver, "body")
        assert "Cliente" in body.text or "cliente" in body.text

    def test_modal_cliente_tiene_campos_clave(self, auth_driver):
        go(auth_driver, "/clientes")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nuevo') or contains(., 'Crear')]"))
        )
        btn.click()
        time.sleep(0.5)
        for campo in ["nombre", "email"]:
            els = auth_driver.find_elements(By.CSS_SELECTOR, f"input[name='{campo}']")
            assert len(els) > 0, f"Campo '{campo}' debe aparecer en modal de cliente"


class TestVentaVista:
    """Verifica la vista de Ventas."""

    def test_titulo_ventas(self, auth_driver):
        go(auth_driver, "/ventas")
        body = find(auth_driver, "body")
        assert "Venta" in body.text or "venta" in body.text


class TestUsuarioVista:
    """Verifica la vista de Usuarios."""

    def test_titulo_usuarios(self, auth_driver):
        go(auth_driver, "/usuarios")
        body = find(auth_driver, "body")
        assert "Usuario" in body.text or "usuario" in body.text
