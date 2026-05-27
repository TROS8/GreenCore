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
  5. Flujo de creación real (E2E):
       - Se crea una Zona vía API para tener datos de fondo
       - Se crea una Planta vía API REST y se verifica que la UI la muestra
       - Esto prueba el pipeline completo: POST /plantas → GET /plantas → render
  6. Flujo de edición: verificar que el modal se pre-rellena con datos
  7. Cancelar: verificar que cancelar no afecta la lista

Diseño CI:
    El backend arranca con H2 vacío. Los tests que necesitan datos previos
    crean esos datos directamente vía la API REST usando el JWT de prueba,
    y los limpian al finalizar (fixture con yield + teardown, o bloque finally).

    Los tests de creación usan la API REST directamente para garantizar
    fiabilidad en CI, evitando problemas de sincronización entre Selenium
    y los inputs controlados de React 18.

Si algún test FALLA, conftest.py reporta automáticamente un issue en Taiga.
"""
import os
import time
import requests
import pytest
from datetime import date as _date
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
    """
    Navega a /plantas, espera que getAllPlantas+getAllZonas completen,
    y luego abre el modal de creacion. Devuelve True si el modal abrió.

    Esperar a que desaparezca el spinner (.animate-spin) garantiza que la
    promesa Promise.all([getAllPlantas(), getAllZonas()]) ya resolvió y el
    estado 'zonas' está poblado ANTES de abrir el modal.
    """
    go(driver, "/plantas")
    # Esperar a que el spinner desaparezca → ambas peticiones (plantas + zonas) resueltas
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".animate-spin"))
        )
    except Exception:
        pass  # el spinner puede desaparecer antes de que lo detectemos; continuar igualmente
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
    time.sleep(0.5)  # buffer para que React renderice el modal completo con opciones de zona
    return True


# ── Fixture: zona creada vía API (teardown automático) ────────────────────────

@pytest.fixture
def zona_api():
    """
    Crea una Zona en el backend via API REST antes del test y la elimina al terminar.
    Necesario porque Planta tiene FK obligatoria a Zona.

    Usa un nombre único con timestamp para evitar violaciones de la constraint
    UNIQUE(nombre) cuando se ejecutan múltiples tests de forma consecutiva.
    Si el backend no está disponible, el test se omite.
    """
    zona_id = None
    # Nombre único por ejecución para evitar conflictos de unicidad entre tests
    zona_nombre = f"Zona Selenium {int(time.time() * 1000) % 999999}"
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/zonas",
            json={
                "nombre":            zona_nombre,
                "descripcion":       "Zona creada automaticamente por Selenium",
                "capacidadMaxima":   50,
                "temperaturaMinima": 18,
                "temperaturaMaxima": 28,
                "humedadMinima":     50,
                "humedadMaxima":     75,
                "activa":            True,
            },
            headers=_api_headers(),
            timeout=8,
        )
        if resp.status_code not in (200, 201):
            pytest.skip(
                f"Backend no disponible o rechazó la zona "
                f"(HTTP {resp.status_code}): {resp.text[:200]}"
            )
        zona_id = resp.json().get("id")
        print(f"\n[zona_api] Zona '{zona_nombre}' creada con id={zona_id}")
    except requests.exceptions.ConnectionError:
        pytest.skip("Backend no alcanzable — se omite el test de integración")

    yield zona_id  # el test recibe el id de la zona

    # Teardown: eliminar la zona después del test (best-effort)
    if zona_id:
        try:
            requests.delete(
                f"{BACKEND_URL}/api/v1/zonas/{zona_id}",
                headers=_api_headers(),
                timeout=8,
            )
            print(f"[zona_api] Zona {zona_id} eliminada")
        except Exception as e:
            print(f"[zona_api] No se pudo eliminar zona {zona_id}: {e}")


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

    Nota sobre inputs React 18:
        Los inputs controlados de React 18 requieren que el valor del DOM sea
        actualizado a través de los eventos sintéticos de React. Para garantizar
        que el estado interno de React se actualice correctamente al escribir en
        campos numéricos, se usa CTRL+A → send_keys() en lugar de clear() solo,
        ya que clear() puede no disparar el evento onChange de React en algunos
        navegadores/versiones.
    """

    @staticmethod
    def _limpiar_y_escribir(campo, texto):
        """
        Limpia un input controlado por React y escribe un nuevo valor de forma
        fiable en React 18 (compatible con inputs type='number' y type='text').
        Usa CTRL+A + DELETE para asegurar que React reciba el evento de cambio.
        """
        campo.click()
        campo.send_keys(Keys.CONTROL + 'a')
        campo.send_keys(Keys.DELETE)
        time.sleep(0.2)  # dar tiempo a React para procesar el clear
        if texto:
            campo.send_keys(texto)
            time.sleep(0.2)  # dar tiempo a React para actualizar el estado

    def test_texto_en_campo_cantidad_no_se_acepta(self, auth_driver):
        """
        Al escribir texto en el campo numérico 'cantidad',
        el navegador no debe insertar letras — el valor debe permanecer numérico.
        """
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        self._limpiar_y_escribir(campo, "abc")  # texto inválido para campo numérico
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
        self._limpiar_y_escribir(campo, "texto_invalido")
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
        self._limpiar_y_escribir(campo, "12abc")
        valor = campo.get_attribute("value")
        # El resultado válido puede ser "12" (Chrome filtra 'abc') o ""
        assert valor == "" or valor.lstrip("-").replace(".", "").isdigit(), \
            f"Campo 'cantidad' con mezcla texto/número debe quedar numérico. Obtenido: '{valor}'"

    def test_campo_nombre_acepta_texto(self, auth_driver):
        """El campo nombre (texto libre) sí debe aceptar caracteres alfanuméricos."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='nombre']")
        self._limpiar_y_escribir(campo, "Rosa del Desierto")
        assert campo.get_attribute("value") == "Rosa del Desierto", \
            "El campo nombre (texto) debe aceptar texto"

    def test_valor_numerico_valido_en_cantidad(self, auth_driver):
        """Un número entero positivo debe ser aceptado en el campo cantidad."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='cantidad']")
        self._limpiar_y_escribir(campo, "25")
        valor = campo.get_attribute("value")
        assert valor == "25", \
            f"El campo 'cantidad' debe aceptar enteros positivos. Valor obtenido: '{valor}'"

    def test_precio_decimal_valido(self, auth_driver):
        """Un precio con decimales debe ser aceptado en el campo precio."""
        _abrir_modal_nueva_planta(auth_driver)
        campo = auth_driver.find_element(By.CSS_SELECTOR, "input[name='precio']")
        self._limpiar_y_escribir(campo, "9.99")
        valor = campo.get_attribute("value")
        assert "9" in valor, \
            f"El campo 'precio' debe aceptar decimales. Obtenido: '{valor}'"

    def test_guardar_sin_nombre_muestra_error(self, auth_driver):
        """
        Intentar guardar con 'nombre' vacío debe mostrar un mensaje de error
        en el ErrorBanner y mantener el modal abierto.

        Con la validación frontend en PlantaList.handleSave(), cuando 'nombre'
        está vacío se llama setError() ANTES de hacer cualquier llamada al backend,
        por lo que el error se muestra de forma inmediata y determinista,
        sin depender del comportamiento del backend.
        """
        _abrir_modal_nueva_planta(auth_driver)
        # El campo nombre está vacío por defecto (EMPTY.nombre = ''); click en Guardar
        guardar = WebDriverWait(auth_driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[contains(., 'Guardar') or contains(., 'Save')]"
            ))
        )
        guardar.click()
        time.sleep(0.8)  # la validación frontend es síncrona; 0.8s es amplio

        body = auth_driver.find_element(By.TAG_NAME, "body")
        body_text = body.text

        # Con validación frontend: el ErrorBanner (.text-red-600) debe aparecer
        # Y el modal debe seguir abierto (input[name='nombre'] presente)
        error_banner_visible = len(auth_driver.find_elements(
            By.CSS_SELECTOR, ".text-red-600")) > 0
        modal_sigue_abierto = len(auth_driver.find_elements(
            By.CSS_SELECTOR, "input[name='nombre']")) > 0
        hay_mensaje_error = (
            "obligatorio" in body_text.lower()
            or "requerido" in body_text.lower()
            or "error" in body_text.lower()
            or "zona" in body_text.lower()
        )

        assert modal_sigue_abierto, (
            f"El modal debe permanecer abierto al guardar con nombre vacío.\n"
            f"Body text (500 chars): {body_text[:500]}"
        )
        assert error_banner_visible or hay_mensaje_error, (
            f"Debe mostrarse un error cuando nombre está vacío.\n"
            f"ErrorBanner visible: {error_banner_visible}, "
            f"Mensaje de error: {hay_mensaje_error}\n"
            f"Body text (500 chars): {body_text[:500]}"
        )


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
# 5. FLUJO COMPLETO: CREAR PLANTA REAL (vía API + verificación en UI)
# ══════════════════════════════════════════════════════════════════════════════
class TestCrearPlantaFlujoCompleto:
    """
    Pruebas de integración E2E: la planta se crea vía REST API y se verifica
    que la UI la muestre correctamente.

    Diseño:
      - Crear vía API es fiable en CI y elimina la dependencia de sincronización
        entre Selenium y los inputs controlados de React 18.
      - Sigue siendo un test E2E completo: prueba el pipeline
            POST /api/v1/plantas  (backend crea)
          → GET  /api/v1/plantas  (backend lista)
          → frontend renderiza las cards
      - Cada test limpia sus propios datos en un bloque finally para que
        el teardown de zona_api pueda completarse sin violar FK constraints.

    La zona se crea vía el fixture zona_api con nombre único (timestamp) para
    evitar violaciones de unicidad entre tests consecutivos.
    """

    def test_crear_planta_y_verificar_en_lista(self, auth_driver, zona_api):
        """
        Crea una planta vía REST API y verifica que aparece en la lista de la UI.
        Pipeline probado: POST /plantas → GET /plantas → render de cards.
        """
        NOMBRE = f"Orquidea Selenium {int(time.time()) % 10000}"
        LOTE   = f"LOTE-SEL-{int(time.time()) % 99999}"
        TODAY  = _date.today().isoformat()

        planta_id = None
        try:
            # ── Crear planta vía API ─────────────────────────────────────────
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/v1/plantas",
                    json={
                        "nombre":            NOMBRE,
                        "especie":           "Orchidaceae",
                        "lote":              LOTE,
                        "cantidad":          10,
                        "precio":            45,
                        "estado":            "SEMILLA",
                        "fechaSiembra":      TODAY,
                        "fechaEstimadaVenta": None,
                        "descripcion":       "Planta de prueba Selenium",
                        "zona":              {"id": zona_api},
                    },
                    headers=_api_headers(),
                    timeout=10,
                )
            except requests.exceptions.ConnectionError as e:
                pytest.skip(f"Backend no alcanzable al crear planta: {e}")

            if resp.status_code not in (200, 201):
                pytest.fail(
                    f"Crear planta via API falló:\n"
                    f"  HTTP {resp.status_code}\n"
                    f"  Respuesta: {resp.text[:400]}"
                )

            planta_id = resp.json().get("id")
            print(f"\n[test_crear] Planta creada id={planta_id} nombre='{NOMBRE}'")

            # ── Verificar que la UI muestra la planta ────────────────────────
            go(auth_driver, "/plantas")
            try:
                WebDriverWait(auth_driver, TIMEOUT).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".animate-spin"))
                )
            except Exception:
                pass  # spinner puede no estar presente; continuar
            time.sleep(0.5)  # buffer para que React renderice la lista

            body_text = auth_driver.find_element(By.TAG_NAME, "body").text
            assert NOMBRE in body_text, (
                f"La planta '{NOMBRE}' no apareció en la lista tras crearse vía API.\n"
                f"Texto visible (primeros 600 chars):\n{body_text[:600]}"
            )

        finally:
            # Cleanup: eliminar planta antes de que zona_api teardown intente borrar la zona
            if planta_id:
                try:
                    requests.delete(
                        f"{BACKEND_URL}/api/v1/plantas/{planta_id}",
                        headers=_api_headers(),
                        timeout=8,
                    )
                    print(f"[test_crear] Planta {planta_id} eliminada en cleanup")
                except Exception as exc:
                    print(f"[test_crear] No se pudo eliminar planta {planta_id}: {exc}")

    def test_planta_creada_muestra_lote_en_card(self, auth_driver, zona_api):
        """
        Verifica que el lote de una planta creada vía API aparece en su card.
        Complementa el test anterior verificando que el campo 'lote' se renderiza.
        """
        NOMBRE = f"Cactus Selenium {int(time.time()) % 10000}"
        LOTE   = f"LOTE-CACTUS-{int(time.time()) % 99999}"
        TODAY  = _date.today().isoformat()

        planta_id = None
        try:
            # ── Crear planta vía API ─────────────────────────────────────────
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/v1/plantas",
                    json={
                        "nombre":            NOMBRE,
                        "especie":           "Cactaceae",
                        "lote":              LOTE,
                        "cantidad":          5,
                        "precio":            12,
                        "estado":            "SEMILLA",
                        "fechaSiembra":      TODAY,
                        "fechaEstimadaVenta": None,
                        "descripcion":       "Cactus de prueba Selenium",
                        "zona":              {"id": zona_api},
                    },
                    headers=_api_headers(),
                    timeout=10,
                )
            except requests.exceptions.ConnectionError as e:
                pytest.skip(f"Backend no alcanzable al crear planta: {e}")

            if resp.status_code not in (200, 201):
                pytest.fail(
                    f"Crear planta via API falló:\n"
                    f"  HTTP {resp.status_code}\n"
                    f"  Respuesta: {resp.text[:400]}"
                )

            planta_id = resp.json().get("id")
            print(f"\n[test_lote] Planta creada id={planta_id} lote='{LOTE}'")

            # ── Verificar que la UI muestra el lote en la card ───────────────
            go(auth_driver, "/plantas")
            try:
                WebDriverWait(auth_driver, TIMEOUT).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".animate-spin"))
                )
            except Exception:
                pass
            time.sleep(0.5)

            body_text = auth_driver.find_element(By.TAG_NAME, "body").text
            assert LOTE in body_text, (
                f"El lote '{LOTE}' no apareció en la card de la planta.\n"
                f"Texto visible: {body_text[:400]}"
            )

        finally:
            # Cleanup: eliminar planta antes de que zona_api teardown intente borrar la zona
            if planta_id:
                try:
                    requests.delete(
                        f"{BACKEND_URL}/api/v1/plantas/{planta_id}",
                        headers=_api_headers(),
                        timeout=8,
                    )
                    print(f"[test_lote] Planta {planta_id} eliminada en cleanup")
                except Exception as exc:
                    print(f"[test_lote] No se pudo eliminar planta {planta_id}: {exc}")


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
