"""
Pruebas CRUD + validación completas para la entidad Planta.
===========================================================
Demuestra el flujo completo que el sistema soporta:

  1. Navegación y carga de la vista
  2. Apertura del modal de creación
  3. Verificación de todos los campos del formulario
  4. VALIDACIÓN de tipos de datos:
       - Campos numéricos (cantidad, precio) rechazan texto
       - Campos de fecha son de tipo 'date'
       - Campo nombre es obligatorio (backend retorna error)
  5. Flujo de creación real:
       - Se crea una Zona vía API para tener datos de fondo
       - Se crea una Planta desde la UI y se verifica que aparece en la lista
  6. Flujo de edición: verificar que el modal se pre-rellena con datos
  7. Cancelar: verificar que canceling no afecta la lista

Diseño CI:
    El backend arranca con H2 vacío. Los tests que necesitan datos previos
    crean esos datos directamente vía la API REST usando el JWT de prueba,
    y los limpian al finalizar (fixture con yield + teardown).

Si algún test FALLA, conftest.py reporta automáticamente un issue en Taiga.
"""
import os
import time
import requests
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from conftest import go, find, TIMEOUT, BASE_URL, BACKEND_URL, generate_test_token


# ── Helpers internos ──────────────────────────────────────────────────────────

def _api_headers():
    """Cabeceras HTTP autenticadas para llamadas directas al backend."""
    token = generate_test_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }


def _abrir_modal_nueva_planta(driver):
    """Navega a /plantas y abre el modal de creacion. Devuelve True si el modal abrió."""
    go(driver, "/plantas")
    btn = WebDriverWait(driver, TIMEOUT).until(
        EC.element_to_be_clickable((By.XPATH,
            "//button[contains(., '+') or contains(., 'Nueva') or contains(., 'Planta') or contains(., 'Crear')]"
        ))
    )
    btn.click()
    # Esperar a que aparezca el input de nombre (señal de que el modal está abierto)
    WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
    )
    time.sleep(0.3)
    return True


# ── Fixture: zona creada vía API (teardown automático) ────────────────────────

@pytest.fixture
def zona_api():
    """
    Crea una Zona en el backend via API REST antes del test y la elimina al terminar.
    Necesario porque Planta tiene FK obligatoria a Zona.
    Si el backend no está disponible, el test se omite.
    """
    zona_id = None
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/zonas",
            json={
                "nombre":           "Zona Selenium Test",
                "descripcion":      "Zona creada automáticamente por Selenium",
                "capacidadMaxima":  50,
                "temperaturaMinima": 18,
                "temperaturaMaxima": 28,
                "humedadMinima":    50,
                "humedadMaxima":    75,
                "activa":           True,
            },
            headers=_api_headers(),
            timeout=8,
        )
        if resp.status_code not in (200, 201):
            pytest.skip(f"Backend no disponible o rechazó la zona (HTTP {resp.status_code})")
        zona_id = resp.json().get("id")
        print(f"\n[zona_api] Zona creada con id={zona_id}")
    except requests.exceptions.ConnectionError:
        pytest.skip("Backend no alcanzable — se omite el test de integración")

    yield zona_id  # el test recibe el id de la zona

    # Teardown: eliminar la zona después del test
    if zona_id:
        try:
            requests.delete(
                f"{BACKEND_URL}/api/v1/zonas/{zona_id}",
                headers=_api_headers(),
                timeout=8,
            )
            print(f"[zona_api] Zona {zona_id} eliminada")
        except Exception:
            pass  # limpieza best-effort


# ══════════════════════════════════════════════════════════════════════════════
# 1. NAVEGACIÓN Y CARGA
# ══════════════════════════════════════════════════════════════════════════════
class TestNavegacionPlantas:
    """La página de plantas carga correctamente y muestra sus elementos clave."""

    def test_pagina_carga_correctamente(self, auth_driver):
        """La ruta /plantas devuelve una página con el título 'Plantas'."""
        go(auth_driver, "/plantas")
        body = find(auth_driver, "body")
        assert "Planta" in body.text or "planta" in body.text, \
            "La página /plantas debe mostrar la palabra 'Planta'"

    def test_titulo_h2_visible(self, auth_driver):
        """Debe existir un encabezado <h2> que contenga 'Plantas'."""
        go(auth_driver, "/plantas")
        headings = auth_driver.find_elements(By.TAG_NAME, "h2")
        textos = [h.text for h in headings if h.is_displayed()]
        assert any("planta" in t.lower() for t in textos), \
            f"Debe haber un h2 con 'Planta'. Encontrado: {textos}"

    def test_boton_nueva_planta_visible(self, auth_driver):
        """El botón para crear nueva planta debe ser visible."""
        go(auth_driver, "/plantas")
        btn = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH,
                "//button[contains(., '+') or contains(., 'Nueva') or contains(., 'Planta')]"
            ))
        )
        assert btn.is_displayed(), "El botón 'Nueva Planta' debe estar visible"

    def test_lista_o_mensaje_vacio(self, auth_driver):
        """Debe mostrar plantas existentes O el mensaje de lista vacía."""
        go(auth_driver, "/plantas")
        time.sleep(1)
        body = auth_driver.find_element(By.TAG_NAME, "body")
        tiene_cards  = len(auth_driver.find_elements(By.CSS_SELECTOR, ".rounded-2xl")) > 0
        tiene_vacio  = any(kw in body.text for kw in ["Sin plantas", "No plants", "registradas"])
        assert tiene_cards or tiene_vacio, \
            "Debe mostrar cards de plantas o mensaje de lista vacía"


# ══════════════════════════════════════════════════════════════════════════════
# 2. MODAL DE CREACIÓN — CAMPOS
# ══════════════════════════════════════════════════════════════════════════════
class TestModalCampos:
    """El modal de nueva planta contiene todos los campos necesarios."""

    def test_modal_abre_al_hacer_click(self, auth_driver):
        """El click en 'Nueva Planta' abre el modal de formulario."""
        _abrir_modal_nueva_planta(auth_driver)
        assert auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']").is_displayed()

    def test_campo_nombre_presente(self, auth_driver):
        """El formulario incluye el campo 'nombre' (texto libre, obligatorio)."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        assert campo.is_displayed()

    def test_campo_especie_presente(self, auth_driver):
        """El formulario incluye el campo 'especie'."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='especie']")
        assert campo.is_displayed()

    def test_campo_cantidad_es_tipo_number(self, auth_driver):
        """El campo 'cantidad' debe ser de tipo numérico (input type=number)."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        assert campo.get_attribute("type") == "number", \
            "El campo 'cantidad' debe ser type='number' para evitar texto"

    def test_campo_precio_es_tipo_number(self, auth_driver):
        """El campo 'precio' debe ser de tipo numérico (input type=number)."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        assert campo.get_attribute("type") == "number", \
            "El campo 'precio' debe ser type='number' para evitar texto"

    def test_campo_fecha_siembra_es_tipo_date(self, auth_driver):
        """El campo 'fechaSiembra' debe ser de tipo date para validar formato."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='fechaSiembra']")
        assert campo.get_attribute("type") == "date", \
            "El campo 'fechaSiembra' debe ser type='date'"

    def test_campo_fecha_venta_es_tipo_date(self, auth_driver):
        """El campo 'fechaEstimadaVenta' debe ser de tipo date."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='fechaEstimadaVenta']")
        assert campo.get_attribute("type") == "date", \
            "El campo 'fechaEstimadaVenta' debe ser type='date'"

    def test_selector_estado_tiene_opciones(self, auth_driver):
        """El selector de estado ofrece las opciones del ciclo de vida."""
        _abrir_modal_nueva_planta(auth_driver)
        select = auth_driver.find_element(By.CSS_SELECTOR, "select[name='estado']")
        opciones = [o.get_attribute("value") for o in select.find_elements(By.TAG_NAME, "option")]
        esperadas = {"SEMILLA", "GERMINANDO", "CRECIMIENTO", "LISTA_VENTA"}
        presentes = esperadas & set(opciones)
        assert presentes == esperadas, \
            f"El selector de estado debe incluir {esperadas}. Encontrado: {opciones}"

    def test_botones_guardar_y_cancelar_presentes(self, auth_driver):
        """El modal debe tener botones de Guardar y Cancelar."""
        _abrir_modal_nueva_planta(auth_driver)
        guardar  = auth_driver.find_element(By.XPATH,
            "//button[contains(., 'Guardar') or contains(., 'Save')]")
        cancelar = auth_driver.find_element(By.XPATH,
            "//button[contains(., 'Cancelar') or contains(., 'Cancel')]")
        assert guardar.is_displayed() and cancelar.is_displayed(), \
            "Los botones Guardar y Cancelar deben estar visibles"


# ══════════════════════════════════════════════════════════════════════════════
# 3. VALIDACIÓN DE TIPOS DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
class TestValidacionCampos:
    """
    Verifica que los campos con tipo específico no acepten valores inválidos.
    Los inputs type='number' rechazan texto; la UI no debe guardar datos corruptos.
    """

    def test_texto_en_campo_cantidad_no_se_acepta(self, auth_driver):
        """
        Al escribir texto en el campo numérico 'cantidad',
        el navegador no debe insertar letras — el valor debe permanecer numérico.
        """
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        campo.clear()
        campo.send_keys("abc")  # texto inválido para campo numérico
        valor = campo.get_attribute("value")
        assert valor == "" or valor.lstrip("-").replace(".", "").isdigit(), \
            f"Campo numérico 'cantidad' no debe aceptar texto. Valor obtenido: '{valor}'"

    def test_texto_en_campo_precio_no_se_acepta(self, auth_driver):
        """
        Al escribir texto en el campo numérico 'precio',
        el navegador no debe insertar letras — el valor debe permanecer numérico.
        """
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        campo.clear()
        campo.send_keys("texto_invalido")
        valor = campo.get_attribute("value")
        assert valor == "" or valor.lstrip("-").replace(".", "").isdigit(), \
            f"Campo numérico 'precio' no debe aceptar texto. Valor obtenido: '{valor}'"

    def test_mezcla_texto_numero_en_cantidad(self, auth_driver):
        """
        Si se mezcla texto y número (ej: '12abc'), solo el número debe quedar
        porque el input type=number filtra los caracteres no numéricos.
        """
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        campo.clear()
        campo.send_keys("12abc")
        valor = campo.get_attribute("value")
        # El resultado válido puede ser "12" (Chrome filtra 'abc') o ""
        assert valor == "" or valor.lstrip("-").replace(".", "").isdigit(), \
            f"Campo 'cantidad' con mezcla texto/número debe quedar numérico. Obtenido: '{valor}'"

    def test_campo_nombre_acepta_texto(self, auth_driver):
        """El campo nombre (texto libre) sí debe aceptar caracteres alfanuméricos."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        campo.clear()
        campo.send_keys("Rosa del Desierto")
        assert campo.get_attribute("value") == "Rosa del Desierto", \
            "El campo nombre (texto) debe aceptar texto"

    def test_valor_numerico_valido_en_cantidad(self, auth_driver):
        """Un número entero positivo debe ser aceptado en el campo cantidad."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        campo.clear()
        campo.send_keys("25")
        assert campo.get_attribute("value") == "25", \
            "El campo 'cantidad' debe aceptar enteros positivos"

    def test_precio_decimal_valido(self, auth_driver):
        """Un precio con decimales debe ser aceptado en el campo precio."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        campo.clear()
        campo.send_keys("9.99")
        valor = campo.get_attribute("value")
        assert "9" in valor, \
            f"El campo 'precio' debe aceptar decimales. Obtenido: '{valor}'"

    def test_guardar_sin_nombre_muestra_error_backend(self, auth_driver):
        """
        Intentar guardar con 'nombre' vacío debe mostrar un mensaje de error
        (el backend rechaza la petición y la UI muestra el ErrorBanner).
        """
        _abrir_modal_nueva_planta(auth_driver)
        # El campo nombre está vacío por defecto; hacer click en Guardar directamente
        guardar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Guardar') or contains(., 'Save')]"
            ))
        )
        guardar.click()
        time.sleep(1.5)  # esperar respuesta del backend

        # Buscar el banner de error (ErrorBanner en ui.jsx) o mensaje de validación
        body = auth_driver.find_element(By.TAG_NAME, "body")
        tiene_error = (
            len(auth_driver.find_elements(By.CSS_SELECTOR, ".text-red-600")) > 0
            or "Error" in body.text
            or "error" in body.text.lower()
            or "requerido" in body.text.lower()
            or "required" in body.text.lower()
        )
        # O bien el modal sigue abierto (no guardó)
        modal_sigue_abierto = len(auth_driver.find_elements(
            By.CSS_SELECTOR, "input[name='nombre']")) > 0

        assert tiene_error or modal_sigue_abierto, \
            "Guardar sin nombre debe mostrar error O mantener el modal abierto"


# ══════════════════════════════════════════════════════════════════════════════
# 4. CANCELAR
# ══════════════════════════════════════════════════════════════════════════════
class TestCancelarModal:
    """Verificar que cancelar el modal no modifica el estado de la lista."""

    def test_cancelar_cierra_el_modal(self, auth_driver):
        """Al hacer click en Cancelar, el modal debe desaparecer."""
        _abrir_modal_nueva_planta(auth_driver)
        cancelar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Cancelar') or contains(., 'Cancel')]"
            ))
        )
        cancelar.click()
        time.sleep(0.5)
        # El campo nombre no debe estar visible tras cancelar
        inputs = auth_driver.find_elements(By.CSS_SELECTOR, "input[name='nombre']")
        assert len(inputs) == 0 or not inputs[0].is_displayed(), \
            "El modal debe cerrarse al hacer click en Cancelar"

    def test_cancelar_con_datos_no_altera_la_lista(self, auth_driver):
        """
        Escribir datos en el modal y luego cancelar no debe crear ningún registro.
        """
        go(auth_driver, "/plantas")
        time.sleep(1)
        # Contar cards antes
        cards_antes = len(auth_driver.find_elements(By.CSS_SELECTOR, ".rounded-2xl.shadow-sm"))

        # Abrir modal, llenar campos y cancelar
        _abrir_modal_nueva_planta(auth_driver)
        auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']").send_keys("Planta Cancelada")
        cancelar = auth_driver.find_element(By.XPATH,
            "//button[contains(., 'Cancelar') or contains(., 'Cancel')]")
        cancelar.click()
        time.sleep(0.8)

        # Contar cards después — debe ser el mismo número
        cards_despues = len(auth_driver.find_elements(By.CSS_SELECTOR, ".rounded-2xl.shadow-sm"))
        assert cards_despues == cards_antes, \
            f"Cancelar no debe crear registros. Antes: {cards_antes}, Después: {cards_despues}"


# ══════════════════════════════════════════════════════════════════════════════
# 5. FLUJO COMPLETO: CREAR PLANTA REAL
# ══════════════════════════════════════════════════════════════════════════════
class TestCrearPlantaFlujoCompleto:
    """
    Prueba de integración end-to-end: crea una planta real desde la UI
    y verifica que aparece en la lista.

    Requiere el backend activo con H2. La zona se crea vía API (fixture zona_api).
    """

    def test_crear_planta_y_verificar_en_lista(self, auth_driver, zona_api):
        """
        Flujo completo:
          1. La zona existe (fixture la creó vía API)
          2. El usuario abre el modal de nueva planta
          3. Completa los campos obligatorios (nombre, especie, lote, cantidad, precio, zona)
             — fechaSiembra ya tiene hoy como valor por defecto en el formulario
          4. Guarda
          5. La planta aparece como card en la lista
        """
        NOMBRE_PLANTA = f"Orquídea Selenium {int(time.time()) % 10000}"
        LOTE_PLANTA   = f"LOTE-SEL-{int(time.time()) % 99999}"

        go(auth_driver, "/plantas")
        time.sleep(1.5)  # esperar carga inicial de zonas

        # Abrir modal
        _abrir_modal_nueva_planta(auth_driver)

        # Rellenar nombre (obligatorio)
        nombre_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        nombre_inp.clear()
        nombre_inp.send_keys(NOMBRE_PLANTA)

        # Rellenar especie (nullable=false en BD)
        especie_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='especie']")
        especie_inp.clear()
        especie_inp.send_keys("Orchidaceae")

        # Rellenar lote único (nullable=false, unique)
        lote_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='lote']")
        lote_inp.clear()
        lote_inp.send_keys(LOTE_PLANTA)

        # Cantidad y precio (nullable=false)
        cantidad_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        cantidad_inp.clear()
        cantidad_inp.send_keys("10")

        precio_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        precio_inp.clear()
        precio_inp.send_keys("45")

        # fechaSiembra ya tiene hoy como valor por defecto (PlantaList.EMPTY → TODAY).
        # No es necesario modificarlo — el backend recibe la fecha predeterminada.

        # Seleccionar la zona (creada por el fixture)
        time.sleep(1.0)  # esperar que getAllZonas() cargue el dropdown
        zona_select = auth_driver.find_element(By.CSS_SELECTOR, "select[name='zonaId']")
        from selenium.webdriver.support.ui import Select as SeleniumSelect
        sel = SeleniumSelect(zona_select)
        opciones_validas = [o for o in sel.options if o.get_attribute("value")]
        if not opciones_validas:
            pytest.skip("Zona no aparece en dropdown aún (getAllZonas aún cargando)")
        sel.select_by_value(opciones_validas[0].get_attribute("value"))
        time.sleep(0.5)  # dejar que React procese el cambio de select

        # Guardar
        guardar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Guardar') or contains(., 'Save')]"
            ))
        )
        guardar.click()

        # Esperar a que el modal se cierre (señal de guardado exitoso)
        WebDriverWait(auth_driver, TIMEOUT + 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
        )
        time.sleep(1.5)  # esperar que la lista se recargue

        # Verificar que la planta aparece en la lista
        body = auth_driver.find_element(By.TAG_NAME, "body")
        assert NOMBRE_PLANTA in body.text, \
            f"La planta '{NOMBRE_PLANTA}' debe aparecer en la lista tras ser creada. " \
            f"Texto visible: {body.text[:600]}"

    def test_planta_creada_muestra_lote_en_card(self, auth_driver, zona_api):
        """
        La card de la planta creada debe mostrar el lote asignado.
        Complementa el test anterior verificando un campo adicional.
        """
        NOMBRE_PLANTA = f"Cactus Selenium {int(time.time()) % 10000}"
        LOTE_PLANTA   = f"LOTE-CACTUS-{int(time.time()) % 99999}"

        go(auth_driver, "/plantas")
        time.sleep(1.5)

        _abrir_modal_nueva_planta(auth_driver)

        nombre_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        nombre_inp.clear()
        nombre_inp.send_keys(NOMBRE_PLANTA)

        especie_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='especie']")
        especie_inp.clear()
        especie_inp.send_keys("Cactaceae")

        lote_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='lote']")
        lote_inp.clear()
        lote_inp.send_keys(LOTE_PLANTA)

        cantidad_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        cantidad_inp.clear()
        cantidad_inp.send_keys("5")

        precio_inp = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        precio_inp.clear()
        precio_inp.send_keys("12")

        # fechaSiembra ya tiene hoy como valor por defecto (PlantaList.EMPTY → TODAY).
        # No es necesario modificarlo — el backend recibe la fecha predeterminada.

        # Seleccionar zona
        time.sleep(1.0)  # esperar que getAllZonas() cargue el dropdown
        zona_select = auth_driver.find_element(By.CSS_SELECTOR, "select[name='zonaId']")
        from selenium.webdriver.support.ui import Select as SeleniumSelect
        sel = SeleniumSelect(zona_select)
        opciones_validas = [o for o in sel.options if o.get_attribute("value")]
        if not opciones_validas:
            pytest.skip("Zona no aparece en dropdown (getAllZonas aún cargando)")
        sel.select_by_value(opciones_validas[0].get_attribute("value"))
        time.sleep(0.5)  # dejar que React procese el cambio de select

        guardar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Guardar') or contains(., 'Save')]"
            ))
        )
        guardar.click()

        WebDriverWait(auth_driver, TIMEOUT + 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
        )
        time.sleep(1.5)

        body = auth_driver.find_element(By.TAG_NAME, "body")
        assert LOTE_PLANTA in body.text, \
            f"El lote '{LOTE_PLANTA}' debe aparecer en la card de la planta creada"


# ══════════════════════════════════════════════════════════════════════════════
# 6. EDICIÓN
# ══════════════════════════════════════════════════════════════════════════════
class TestEdicionPlanta:
    """Verifica que el flujo de edición pre-rellena el formulario con datos existentes."""

    def test_boton_editar_presente_en_cards(self, auth_driver):
        """Las cards de plantas deben tener un botón de editar visible."""
        go(auth_driver, "/plantas")
        time.sleep(1.5)
        botones = auth_driver.find_elements(By.XPATH,
            "//button[contains(., 'Editar') or contains(., 'Edit')]")
        if len(botones) == 0:
            pytest.skip("No hay plantas cargadas para editar (backend vacío)")
        assert botones[0].is_displayed(), "El botón Editar debe estar visible en las cards"

    def test_editar_abre_modal_con_datos_precargados(self, auth_driver):
        """
        Al hacer click en Editar, el modal debe abrirse con el nombre
        de la planta ya relleno (datos pre-cargados desde el backend).
        """
        go(auth_driver, "/plantas")
        time.sleep(1.5)
        botones = auth_driver.find_elements(By.XPATH,
            "//button[contains(., 'Editar') or contains(., 'Edit')]")
        if len(botones) == 0:
            pytest.skip("No hay plantas cargadas (backend vacío)")

        botones[0].click()
        nombre_input = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='nombre']"))
        )
        nombre_valor = nombre_input.get_attribute("value")
        assert nombre_valor != "", \
            "El campo nombre debe estar pre-relleno al abrir el modal de edición"
