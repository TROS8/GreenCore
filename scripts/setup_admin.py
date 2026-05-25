"""
GreenCore - Bootstrap de usuario ADMIN en produccion.

El sistema GreenCore usa solo Google OAuth2, por lo que el primer usuario
siempre entra como OPERARIO. Este script automatiza la promocion a ADMIN
conectandose directamente a la base de datos PostgreSQL de Render.

Flujo:
  1. Conecta a PostgreSQL usando DATABASE_URL del .env
  2. Lista todos los usuarios registrados
  3. Busca el email configurado en ADMIN_EMAIL
  4. Si existe: actualiza rol a ADMIN
  5. Si no existe: muestra instrucciones para hacer login con Google primero
  6. Verifica el resultado y reporta

Uso:
  1. Copia .env.example a .env y rellena los valores
  2. Obtener DATABASE_URL: Render Dashboard -> PostgreSQL -> External Database URL
  3. python setup_admin.py

Dependencias:
  pip install -r requirements.txt
"""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass  # acepta variables de entorno del sistema

try:
    import pg8000
    import pg8000.native
except ImportError:
    print("ERROR: pg8000 no instalado. Ejecuta: pip install -r scripts/requirements.txt")
    sys.exit(1)

from urllib.parse import urlparse

# ── Configuracion ──────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "")
ADMIN_EMAIL  = os.getenv("ADMIN_EMAIL",  "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL no configurado en .env")
    print("  Obtenerla en: Render Dashboard -> Tu PostgreSQL -> External Database URL")
    print("  Formato: postgresql://user:password@host.render.com/dbname")
    sys.exit(1)

if not ADMIN_EMAIL:
    print("ERROR: ADMIN_EMAIL no configurado en .env")
    sys.exit(1)

# Normalizar prefijo (Render a veces entrega 'postgres://')
db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Parsear URL para pg8000
_parsed  = urlparse(db_url)
DB_HOST  = _parsed.hostname
DB_PORT  = _parsed.port or 5432
DB_NAME  = _parsed.path.lstrip("/")
DB_USER  = _parsed.username
DB_PASS  = _parsed.password

# ── Conexion ───────────────────────────────────────────────────────────────────

print("=" * 55)
print("  GreenCore - Setup ADMIN")
print("=" * 55)
print(f"  Email objetivo: {ADMIN_EMAIL}")
print(f"  Base de datos : {db_url.split('@')[-1]}")   # oculta credenciales
print()

try:
    import ssl as _ssl
    ssl_ctx = _ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode    = _ssl.CERT_NONE

    conn = pg8000.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        ssl_context=ssl_ctx,
        timeout=15,
    )
    conn.autocommit = False
    print("[OK] Conexion a PostgreSQL establecida")
except Exception as e:
    print(f"[ERROR] No se pudo conectar a PostgreSQL: {e}")
    print()
    print("Posibles causas:")
    print("  - DATABASE_URL incorrecta (verifica en Render Dashboard)")
    print("  - La IP de tu maquina no esta autorizada en Render")
    print("    -> Render Dashboard -> PostgreSQL -> Access Control -> Allow 0.0.0.0/0")
    sys.exit(1)

def query(sql, params=None):
    """Ejecuta una consulta y retorna filas como lista de dicts."""
    cur = conn.cursor()
    cur.execute(sql, params or [])
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = [dict(zip(cols, row)) for row in (cur.fetchall() or [])]
    return rows

def execute(sql, params=None):
    """Ejecuta un comando DML y retorna el numero de filas afectadas."""
    cur = conn.cursor()
    cur.execute(sql, params or [])
    return cur.rowcount


# ── Listar todos los usuarios ──────────────────────────────────────────────────

usuarios = query("SELECT id, email, nombre, rol, activo FROM usuarios ORDER BY id")

print()
print(f"Usuarios registrados ({len(usuarios)}):")
print("-" * 55)
for u in usuarios:
    marca  = " <-- objetivo" if u["email"] == ADMIN_EMAIL else ""
    estado = "activo" if u["activo"] else "inactivo"
    print(f"  [{u['id']:>3}] {u['email']:<35} {u['rol']:<12} {estado}{marca}")
print("-" * 55)
print()

# ── Buscar el usuario objetivo ─────────────────────────────────────────────────

filas_obj = query("SELECT id, email, nombre, rol FROM usuarios WHERE email = %s", [ADMIN_EMAIL])
objetivo  = filas_obj[0] if filas_obj else None

if not objetivo:
    print(f"[AVISO] El usuario '{ADMIN_EMAIL}' no existe aun en la base de datos.")
    print()
    print("Pasos para registrarlo:")
    print("  1. Abre el frontend en produccion")
    print("     https://greencore-frontend.onrender.com")
    print(f"  2. Inicia sesion con Google usando la cuenta: {ADMIN_EMAIL}")
    print("  3. Vuelve a ejecutar este script")
    conn.close()
    sys.exit(0)

# ── Verificar si ya es ADMIN ───────────────────────────────────────────────────

if objetivo["rol"] == "ADMIN":
    print(f"[OK] '{ADMIN_EMAIL}' ya tiene rol ADMIN. No se requiere ninguna accion.")
    conn.close()
    sys.exit(0)

# ── Promover a ADMIN ───────────────────────────────────────────────────────────

print(f"Promoviendo '{ADMIN_EMAIL}'  {objetivo['rol']} -> ADMIN ...")

try:
    filas = execute("UPDATE usuarios SET rol = 'ADMIN' WHERE email = %s", [ADMIN_EMAIL])
    conn.commit()

    if filas == 1:
        print("[OK] Rol actualizado correctamente (1 fila modificada)")
    else:
        print(f"[AVISO] Se esperaba 1 fila pero se modificaron {filas}")

except Exception as e:
    conn.rollback()
    print(f"[ERROR] No se pudo actualizar el rol: {e}")
    conn.close()
    sys.exit(1)

# ── Verificacion final ─────────────────────────────────────────────────────────

filas_ver = query("SELECT id, email, nombre, rol FROM usuarios WHERE email = %s", [ADMIN_EMAIL])
verificado = filas_ver[0]
conn.close()

print()
print("Verificacion final:")
print(f"  ID     : {verificado['id']}")
print(f"  Email  : {verificado['email']}")
print(f"  Nombre : {verificado['nombre']}")
print(f"  Rol    : {verificado['rol']}")
print()

if verificado["rol"] == "ADMIN":
    print("[EXITO] El usuario ahora es ADMIN.")
    print()
    print("Proximos pasos:")
    print("  1. Cierra sesion en el frontend")
    print("  2. Vuelve a iniciar sesion con Google")
    print("     -> El nuevo JWT contendra rol=ADMIN")
    print("  3. Ya tendras acceso completo al dashboard de administracion")
else:
    print(f"[ERROR] El rol sigue siendo '{verificado['rol']}'. Algo salio mal.")
    sys.exit(1)
