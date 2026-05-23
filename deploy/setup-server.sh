#!/usr/bin/env bash
# =============================================================================
# GreenCore — Script de configuración inicial del servidor de producción
# Sistema: Ubuntu 22.04 LTS
# Ejecutar como root: sudo bash setup-server.sh
# =============================================================================
set -euo pipefail
GREENCORE_USER="greencore"
APP_DIR="/opt/greencore/app"
WWW_DIR="/var/www/greencore"

echo "============================================="
echo " GreenCore — Setup servidor de producción"
echo "============================================="

# ── 1. Actualizar sistema ─────────────────────────────────────────────────────
echo "[1/8] Actualizando paquetes del sistema..."
apt-get update -q && apt-get upgrade -y -q

# ── 2. Instalar Java 17 ───────────────────────────────────────────────────────
echo "[2/8] Instalando OpenJDK 17..."
apt-get install -y -q openjdk-17-jdk-headless
java -version

# ── 3. Instalar Nginx ─────────────────────────────────────────────────────────
echo "[3/8] Instalando Nginx..."
apt-get install -y -q nginx
systemctl enable nginx

# ── 4. Instalar PostgreSQL ────────────────────────────────────────────────────
echo "[4/8] Instalando PostgreSQL 15..."
apt-get install -y -q postgresql postgresql-contrib
systemctl enable postgresql
systemctl start postgresql

# Crear base de datos y usuario
echo "[4/8] Creando base de datos greencore..."
sudo -u postgres psql <<SQL
CREATE USER greencore_user WITH PASSWORD 'CHANGE_ME_PASSWORD';
CREATE DATABASE greencore OWNER greencore_user ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE greencore TO greencore_user;
SQL

# ── 5. Crear usuario del sistema ──────────────────────────────────────────────
echo "[5/8] Creando usuario del sistema '$GREENCORE_USER'..."
if ! id "$GREENCORE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/greencore "$GREENCORE_USER"
fi

# ── 6. Crear directorios ──────────────────────────────────────────────────────
echo "[6/8] Creando directorios de la aplicación..."
mkdir -p "$APP_DIR"
mkdir -p "$WWW_DIR"
chown -R "$GREENCORE_USER:$GREENCORE_USER" "/opt/greencore"
chown -R www-data:www-data "$WWW_DIR"

# Crear archivo de variables de entorno (RELLENAR MANUALMENTE)
cat > "$APP_DIR/greencore.env" <<ENV
# !! EDITAR CON VALORES REALES ANTES DE ARRANCAR !!
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/greencore
SPRING_DATASOURCE_USERNAME=greencore_user
SPRING_DATASOURCE_PASSWORD=CHANGE_ME_PASSWORD
JWT_SECRET=CHANGE_ME_JWT_SECRET_VERY_LONG_AND_RANDOM
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-gmail-app-password
ENV
chmod 600 "$APP_DIR/greencore.env"
chown "$GREENCORE_USER:$GREENCORE_USER" "$APP_DIR/greencore.env"
echo "⚠  Editar $APP_DIR/greencore.env con los valores reales!"

# ── 7. Instalar servicio systemd ──────────────────────────────────────────────
echo "[7/8] Instalando servicio systemd greencore-backend..."
cp "$(dirname "$0")/greencore-backend.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable greencore-backend
echo "Servicio registrado. Arrancar con: sudo systemctl start greencore-backend"

# ── 8. Configurar Nginx ───────────────────────────────────────────────────────
echo "[8/8] Configurando Nginx..."
cp "$(dirname "$0")/nginx-greencore.conf" /etc/nginx/sites-available/greencore
ln -sf /etc/nginx/sites-available/greencore /etc/nginx/sites-enabled/greencore
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ── Configurar clave SSH para deploy desde GitHub Actions ────────────────────
echo ""
echo "============================================="
echo " CONFIGURACIÓN DE DEPLOY POR SSH"
echo "============================================="
echo ""
echo "1. Genera un par de claves SSH para el deploy:"
echo "   ssh-keygen -t ed25519 -C 'greencore-github-actions' -f ~/.ssh/greencore_deploy"
echo ""
echo "2. Añade la clave pública al servidor:"
echo "   cat ~/.ssh/greencore_deploy.pub >> /home/$GREENCORE_USER/.ssh/authorized_keys"
echo ""
echo "3. Configura los siguientes GitHub Secrets en:"
echo "   https://github.com/TROS8/GreenCore/settings/secrets/actions"
echo ""
echo "   DEPLOY_HOST  → IP o dominio del servidor"
echo "   DEPLOY_USER  → $GREENCORE_USER"
echo "   DEPLOY_KEY   → contenido de ~/.ssh/greencore_deploy (clave PRIVADA)"
echo ""
echo "============================================="
echo " INSTALACIÓN COMPLETADA"
echo "============================================="
echo ""
echo "Próximos pasos:"
echo "  1. Editar $APP_DIR/greencore.env con credenciales reales"
echo "  2. Editar /etc/nginx/sites-available/greencore (reemplazar TU_DOMINIO_O_IP)"
echo "  3. Añade la clave SSH pública al servidor (ver arriba)"
echo "  4. Configurar GitHub Secrets (ver arriba)"
echo "  5. Hacer push a main → el CI desplegará automáticamente"
