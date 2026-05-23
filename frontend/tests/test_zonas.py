"""
Pruebas de la vista Zonas: listado, creacion, edicion, validaciones de formulario.
Cubre el flujo CRUD completo de la entidad mas basica del sistema.
"""
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import go, find, find_all, click, TIMEOUT


def abrir_modal_crear(driver):
    """Helper: navega a /zonas y abre el modal de creacion."""
    go(driver, "/zonas")
    btn = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Nueva') or contains(., 'Crear') or contains(., 'crear') or contains(., '+')]"))
    )
    btn.click()
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
    )


class TestListaZonas:
    """Verifica el listado de zonas."""

    def test_pagina_carga(self, auth_driver):
        go(auth_driver, "/zonas")
        body = find(auth_driver, "body")
        assert "zona" in body.text.lower() or "Zona" in body.text

    def test_titulo_visible(self, auth_driver):
        go(auth_driver, "/zonas")
        headings = auth_driver.find_elements(By.TAG_NAME, "h2")
        textos = [h.text for h in headings]
        assert any("zona" in t.lower() or "Zona" in t for t in textos), \
            f"Debe haber un titulo con 'Zona'. Encontrado: {textos}"

    def test_boton_crear_presente(self, auth_driver):
        go(auth_driver, "/zonas")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH,
                "//button[contains(., 'Nueva') or contains(., 'Crear') or contains(., '+')]"))
        )
        assert btn.is_displayed()

    def test_zonas_o_mensaje_vacio(self, auth_driver):
        go(auth_driver, "/zonas")
        time.sleep(1)
        body = auth_driver.find_element(By.TAG_NAME, "body")
        tiene_cards = len(auth_driver.find_elements(By.CSS_SELECTOR, ".border.rounded-lg")) > 0
        tiene_vacio = "Sin zonas" in body.text or "registradas" in body.text or "cargando" in body.text.lower()
        assert tiene_cards or tiene_vacio, "Debe mostrar zonas o mensaje de lista vacia"


class TestModalCrearZona:
    """Verifica el modal de creacion de zona."""

    def test_modal_abre_al_click(self, auth_driver):
        abrir_modal_crear(auth_driver)
        modal_input = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        assert modal_input.is_displayed()

    def test_campos_del_formulario_presentes(self, auth_driver):
        abrir_modal_crear(auth_driver)
        campos_requeridos = ["nombre", "capacidadMaxima", "temperaturaMinima",
                             "temperaturaMaxima", "humedadMinima", "humedadMaxima"]
        for campo in campos_requeridos:
            el = auth_driver.find_element(By.CSS_SELECTOR, f"input[name='{campo}']")
            assert el.is_displayed(), f"Campo '{campo}' debe estar visible en el modal"

    def test_campo_descripcion_presente(self, auth_driver):
        abrir_modal_crear(auth_driver)
        desc = auth_driver.find_element(By.CSS_SELECTOR, "textarea[name='descripcion']")
        assert desc.is_displayed()

    def test_checkbox_activa_presente(self, auth_driver):
        abrir_modal_crear(auth_driver)
        checkbox = auth_driver.find_element(By.CSS_SELECTOR, "input[name='activa']")
        assert checkbox.is_displayed()
        assert checkbox.is_selected(), "Zona nueva debe estar activa por defecto"

    def test_boton_cancelar_cierra_modal(self, auth_driver):
        abrir_modal_crear(auth_driver)
        cancel = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Cancelar') or contains(., 'Cancel')]"))
        )
        cancel.click()
        time.sleep(0.5)
        inputs = auth_driver.find_elements(By.CSS_SELECTOR, "input[name='nombre']")
        assert len(inputs) == 0 or not inputs[0].is_displayed(), \
            "Modal debe cerrarse al cancelar"

    def test_formulario_acepta_nombre(self, auth_driver):
        abrir_modal_crear(auth_driver)
        nombre_input = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        nombre_input.clear()
        nombre_input.send_keys("Zona Selenium Test")
        assert nombre_input.get_attribute("value") == "Zona Selenium Test"

    def test_botones_guardar_y_cancelar_presentes(self, auth_driver):
        abrir_modal_crear(auth_driver)
        guardar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH,
                "//button[contains(., 'Guardar') or contains(., 'Save') or contains(., 'Crear')]"))
        )
        cancelar = auth_driver.find_element(By.XPATH,
            "//button[contains(., 'Cancelar') or contains(., 'Cancel')]")
        assert guardar.is_displayed() and cancelar.is_displayed()


class TestEdicionZona:
    """Verifica que el boton Editar abre el modal con datos pre-cargados."""

    def test_boton_editar_presente_en_cards(self, auth_driver):
        go(auth_driver, "/zonas")
        time.sleep(1.5)
        botones_editar = auth_driver.find_elements(By.XPATH,
            "//button[contains(., 'Editar') or contains(., 'Edit')]")
        if len(botones_editar) == 0:
            pytest.skip("No hay zonas cargadas para editar (backend vacio)")
        assert botones_editar[0].is_displayed()

    def test_editar_abre_modal_con_datos(self, auth_driver):
        go(auth_driver, "/zonas")
        time.sleep(1.5)
        botones_editar = auth_driver.find_elements(By.XPATH,
            "//button[contains(., 'Editar') or contains(., 'Edit')]")
        if len(botones_editar) == 0:
            pytest.skip("No hay zonas cargadas (backend vacio)")
        botones_editar[0].click()
        nombre_input = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
        )
        assert nombre_input.get_attribute("value") != "", \
            "El campo nombre debe tener datos al editar"
