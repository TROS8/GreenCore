# ── Etapa 1: Build ────────────────────────────────────────────────────────────
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app

# Copiar pom.xml primero para cachear dependencias
COPY pom.xml .
RUN mvn -B dependency:go-offline -q

# Copiar fuentes y compilar (sin tests)
COPY src ./src
RUN mvn -B package -DskipTests -q

# ── Etapa 2: Runtime ──────────────────────────────────────────────────────────
# Usar jammy (Ubuntu 22.04) en vez de Alpine: tiene CA certs completos para SSL con Supabase
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

# Copiar el JAR generado
COPY --from=build /app/target/greencore-*.jar app.jar

# Puerto que expone la app (Render usa $PORT)
EXPOSE 8080

# Arranque: respeta $PORT de Render
ENTRYPOINT ["sh", "-c", "java -jar app.jar --server.port=${PORT:-8080}"]
