"""Script para crear las 18 user stories de GreenCore en Taiga."""
import requests
import time

TOKEN      = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc5NTIzMzAzLCJqdGkiOiIzZmViMDBmMTgwODY0MzY1OTdmOTZlODBhYzk2NmQ2ZSIsInVzZXJfaWQiOjkxNDc2OH0.K8mZAbRQaoeSzrcjS-eXQaArNE8M6UKaSINtgh8HUgJSy_YjtueYwSnMnlZQymtAlZk2xHw8j1s59C8_n8t9JSTTgsoWchlzfFNxZz_xiC4FHvLxEzVuldwFlu2qoFmp3VR-eJpvpczmoIOhSbRDGPjneWb5m-DM5dfaG60o0QNUWCQlO8pBeI1rK1ntB3iFIXiMlSElR7imZj54_nUpJHOLxXzyesn7Uy1Qra_kt_vSMYMeRB5T8z8KuLHBURKgdcYxfNFBpt3Xr9zQemKXzuBZDdawpcN3E5a3bbKX6uy1PrDB00wZbCmDfZd4bD9qmb9AV-9uQgQB56WtVA59_w"
PROJECT_ID = 1792551
DONE       = 10875831
IN_PROG    = 10875829

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

STORIES = [
    {
        "subject": "Gestion de zonas del invernadero",
        "status": DONE,
        "description": (
            "Como administrador, quiero gestionar zonas fisicas del invernadero.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] CRUD completo de zonas\n"
            "- [x] Validacion de temperaturas y humedades min/max\n"
            "- [x] Endpoint GET /api/v1/zonas retorna lista\n"
            "- [x] Zona tiene: nombre, descripcion, capacidadMaxima, activa"
        ),
    },
    {
        "subject": "Registro y autenticacion de usuarios",
        "status": DONE,
        "description": (
            "Como usuario, quiero registrarme y autenticarme de forma segura.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Login con JWT HMAC256\n"
            "- [x] Token expira en 168 horas\n"
            "- [x] Endpoint POST /api/v1/auth/login retorna token\n"
            "- [x] Roles: ADMIN, OPERARIO, VENDEDOR"
        ),
    },
    {
        "subject": "OAuth2 con Google",
        "status": DONE,
        "description": (
            "Como usuario, quiero iniciar sesion con mi cuenta Google.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Flujo OAuth2 con Google completo\n"
            "- [x] Al autenticar con Google se genera JWT propio\n"
            "- [x] OAuth2SuccessHandler redirige al frontend con token\n"
            "- [x] Spring Security configurado estateless"
        ),
    },
    {
        "subject": "Gestion de plantas por zona",
        "status": DONE,
        "description": (
            "Como operario, quiero registrar plantas en cada zona.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] CRUD de plantas asociadas a una zona\n"
            "- [x] Planta tiene especie, fechaSiembra, estado\n"
            "- [x] Estados: SEMILLA, PLANTULA, ADULTA, COSECHADA\n"
            "- [x] Endpoint GET /api/v1/plantas?zonaId={id}"
        ),
    },
    {
        "subject": "Sensores IoT y lecturas en tiempo real",
        "status": DONE,
        "description": (
            "Como sistema, quiero registrar lecturas de sensores IoT.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] CRUD de sensores por zona\n"
            "- [x] Tipos: TEMPERATURA, HUMEDAD, LUZ, CO2, PH\n"
            "- [x] Endpoint POST /api/v1/sensores/{id}/lecturas\n"
            "- [x] Lectura registra valor, unidad y timestamp"
        ),
    },
    {
        "subject": "Sistema de alertas ambientales",
        "status": DONE,
        "description": (
            "Como administrador, quiero alertas cuando los valores salen del rango.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Alerta generada al registrar lectura fuera de rango\n"
            "- [x] Tipos: TEMPERATURA, HUMEDAD, PLAGA, RIEGO, OTRO\n"
            "- [x] Severidades: BAJA, MEDIA, ALTA, CRITICA\n"
            "- [x] Endpoint PATCH /api/v1/alertas/{id}/marcar-leida"
        ),
    },
    {
        "subject": "Notificaciones por email Gmail SMTP",
        "status": DONE,
        "description": (
            "Como administrador, quiero emails cuando hay alertas criticas.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Spring Boot Mail configurado con Gmail SMTP\n"
            "- [x] Email enviado al crear alerta ALTA o CRITICA\n"
            "- [x] Asunto y cuerpo internacionalizados\n"
            "- [x] Configurable via variables de entorno"
        ),
    },
    {
        "subject": "Gestion de clientes",
        "status": DONE,
        "description": (
            "Como vendedor, quiero gestionar el catalogo de clientes.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] CRUD completo de clientes\n"
            "- [x] Cliente tiene nombre, email, telefono, tipo\n"
            "- [x] Tipos: MAYORISTA, MINORISTA\n"
            "- [x] Email unico por cliente"
        ),
    },
    {
        "subject": "Registro de ventas con control de stock",
        "status": DONE,
        "description": (
            "Como vendedor, quiero registrar ventas de plantas.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Venta asocia cliente, planta y cantidad\n"
            "- [x] Validacion de stock disponible\n"
            "- [x] Error si cantidad > stock\n"
            "- [x] Filtro por fecha: GET /api/v1/ventas?desde=&hasta="
        ),
    },
    {
        "subject": "Dashboard React con metricas del invernadero",
        "status": DONE,
        "description": (
            "Como usuario, quiero ver un dashboard con el estado del invernadero.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Dashboard con estadisticas de zonas, plantas, sensores\n"
            "- [x] Componentes React con TailwindCSS\n"
            "- [x] Estado global con Zustand\n"
            "- [x] Ruta protegida: solo usuarios autenticados"
        ),
    },
    {
        "subject": "Internacionalizacion ES/EN i18n",
        "status": DONE,
        "description": (
            "Como usuario, quiero usar la aplicacion en espanol o ingles.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Backend: AcceptHeaderLocaleResolver + messages.properties\n"
            "- [x] Frontend: selector de idioma EN/ES en navbar\n"
            "- [x] Archivos generados automaticamente desde modelo.json\n"
            "- [x] Soporte cabecera Accept-Language y ?lang=en"
        ),
    },
    {
        "subject": "Documentacion OpenAPI Swagger UI",
        "status": DONE,
        "description": (
            "Como desarrollador, quiero explorar la API con Swagger UI.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Springdoc OpenAPI con @Tag, @Operation, @ApiResponse\n"
            "- [x] Swagger UI disponible en /swagger-ui/index.html\n"
            "- [x] Todos los endpoints documentados\n"
            "- [x] Javadoc en todos los archivos Java"
        ),
    },
    {
        "subject": "Pipeline CI/CD con GitHub Actions",
        "status": DONE,
        "description": (
            "Como equipo, queremos que el codigo se construya y pruebe automaticamente.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Jobs: generate, backend, frontend, selenium, taiga, deploy\n"
            "- [x] Backend: mvn package con JUnit\n"
            "- [x] Frontend: npm ci + npm run build\n"
            "- [x] Deploy via SSH + rsync al servidor"
        ),
    },
    {
        "subject": "Tests Selenium end-to-end",
        "status": DONE,
        "description": (
            "Como QA, quiero tests automatizados de la interfaz.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Tests con Selenium + PyTest + Chrome headless\n"
            "- [x] Autenticacion via JWT inyectado en localStorage\n"
            "- [x] Cobertura: auth, navbar, zonas, entities, dashboard\n"
            "- [x] Reporte HTML como artifact de CI"
        ),
    },
    {
        "subject": "Generador de codigo desde modelo.json",
        "status": DONE,
        "description": (
            "Como desarrollador, quiero generar codigo automaticamente desde el modelo.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] generate.py lee modelo.json y genera backend + frontend + i18n\n"
            "- [x] Genera messages.properties y messages_en.properties\n"
            "- [x] Integrado como primer job en GitHub Actions\n"
            "- [x] Sin edicion manual de archivos generados"
        ),
    },
    {
        "subject": "Conectividad y trazabilidad con Taiga",
        "status": DONE,
        "description": (
            "Como gestor, quiero verificar el estado del proyecto en Taiga desde CI.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] taiga_checker.py autentica con Taiga REST API\n"
            "- [x] Lista user stories y valida criterios de aceptacion\n"
            "- [x] Genera reporte HTML con metricas de completitud\n"
            "- [x] Integrado en GitHub Actions como job independiente"
        ),
    },
    {
        "subject": "Deploy automatico en servidor de produccion",
        "status": IN_PROG,
        "description": (
            "Como DevOps, quiero que cada push a main se despliegue automaticamente.\n\n"
            "Criterios de aceptacion:\n"
            "- [ ] SSH deploy configurado con secrets en GitHub Actions\n"
            "- [ ] rsync JAR backend y dist frontend al servidor\n"
            "- [ ] systemctl restart greencore-backend\n"
            "- [x] Health-check POST-deploy en /actuator/health"
        ),
    },
    {
        "subject": "Modelo ER y diccionario de datos",
        "status": DONE,
        "description": (
            "Como arquitecto, quiero documentar el modelo de datos.\n\n"
            "Criterios de aceptacion:\n"
            "- [x] Diagrama ER en Mermaid con 8 entidades\n"
            "- [x] Diccionario de datos con tipos, constraints y relaciones\n"
            "- [x] Documentos Word exportados (diagrama_er.docx, diccionario_datos.docx)\n"
            "- [x] Seed SQL con datos de ejemplo"
        ),
    },
]

print(f"Creando {len(STORIES)} user stories en GreenCore (ID {PROJECT_ID})...")
print()

created = 0
errors  = 0
for i, story in enumerate(STORIES, 1):
    payload = {
        "project":     PROJECT_ID,
        "subject":     story["subject"],
        "status":      story["status"],
        "description": story["description"],
    }
    resp = requests.post(
        "https://api.taiga.io/api/v1/userstories",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )
    if resp.status_code == 201:
        data   = resp.json()
        ref    = data.get("ref", "?")
        closed = data.get("is_closed", False)
        tag    = "[DONE]" if closed else "[WIP] "
        print(f"  {tag} #{ref:>2}  {story['subject']}")
        created += 1
    else:
        print(f"  [ERR]       {story['subject'][:50]} -> HTTP {resp.status_code}: {resp.text[:80]}")
        errors += 1
    time.sleep(0.5)

print()
print(f"Resultado: {created} creadas, {errors} errores")
