/**
 * GreenCore — Sistema integral de gestión de invernadero
 * Punto de entrada principal de la aplicación Spring Boot.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Clase principal que arranca el contexto de Spring Boot para GreenCore.
 * Incluye: JPA, Security, OAuth2, Mail, OpenAPI (Springdoc).
 * <p>
 * {@code @EnableScheduling} activa los cron jobs definidos en
 * {@link com.greencore.tasks.GreenCoreTasks}:
 * polling de sensores cada 5 min y reporte diario a las 7am.
 * </p>
 */
@SpringBootApplication
@EnableScheduling
public class GreenCoreApplication {

    /**
     * Punto de entrada de la JVM. Inicializa el contexto de Spring Boot.
     *
     * @param args argumentos de línea de comandos (no utilizados)
     */
    public static void main(String[] args) {
        SpringApplication.run(GreenCoreApplication.class, args);
    }
}
