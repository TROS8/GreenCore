/**
 * GreenCore - Sistema de gestion de invernadero
 * Tareas programadas: simulacion de lecturas de sensores y reporte diario.
 *
 * Cron jobs definidos en modelo.json - automation:
 *   sensor_polling_cron : cada 5 minutos
 *   reporte_diario_cron : diario a las 7:00 am
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.tasks;

import com.greencore.model.EstadoSensor;
import com.greencore.model.LecturaSensor;
import com.greencore.model.Sensor;
import com.greencore.repository.SensorRepository;
import com.greencore.service.AlertaService;
import com.greencore.service.EmailNotificationService;
import com.greencore.service.SensorService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Componente Spring que ejecuta las tareas programadas del sistema GreenCore.
 * Requiere @EnableScheduling en la clase principal de la aplicacion.
 */
@Component
public class GreenCoreTasks {

    private static final Logger log = LoggerFactory.getLogger(GreenCoreTasks.class);

    private final SensorRepository sensorRepository;
    private final SensorService sensorService;
    private final AlertaService alertaService;
    private final EmailNotificationService emailService;

    /** Correo del administrador para el reporte diario (spring.mail.username). */
    @Value("${spring.mail.username:}")
    private String adminEmail;

    /** URL del frontend para incluir en correos. */
    @Value("${app.frontend-url:https://greencore-frontend.onrender.com}")
    private String frontendUrl;

    /**
     * @param sensorRepository repositorio de sensores (para listar activos)
     * @param sensorService    servicio de sensores (registrarLectura con logica completa)
     * @param alertaService    servicio de alertas (para el reporte diario)
     * @param emailService     servicio de correo Gmail
     */
    public GreenCoreTasks(SensorRepository sensorRepository,
                          SensorService sensorService,
                          AlertaService alertaService,
                          EmailNotificationService emailService) {
        this.sensorRepository = sensorRepository;
        this.sensorService    = sensorService;
        this.alertaService    = alertaService;
        this.emailService     = emailService;
    }

    // =========================================================================
    // Tarea 1 - Polling de sensores cada 5 minutos
    // =========================================================================

    /**
     * Simula la lectura periodica de todos los sensores ACTIVOS del invernadero.
     *
     * Para cada sensor con valorActual != null calcula una variacion aleatoria
     * de +/-8% y llama a SensorService#registrarLectura, que se encarga de:
     *   - Calcular fueraDeRango contra los umbrales del sensor.
     *   - Actualizar valorActual y ultimaLectura del sensor.
     *   - Crear una Alerta automatica si el valor esta fuera de rango.
     *   - Enviar correo Gmail si la alerta es de nivel CRITICO.
     *
     * Cron: cada 5 minutos (expresion: 0 slash-5 * * * *)
     */
    @Scheduled(cron = "0 */5 * * * *")
    public void pollSensores() {
        List<Sensor> activos = sensorRepository.findAll().stream()
                .filter(s -> EstadoSensor.ACTIVO.equals(s.getEstado())
                          && s.getValorActual() != null)
                .toList();

        if (activos.isEmpty()) {
            log.debug("[GreenCore] pollSensores: no hay sensores activos con valor base.");
            return;
        }

        log.info("[GreenCore] pollSensores: procesando {} sensores activos...", activos.size());
        int alertasGeneradas = 0;

        for (Sensor sensor : activos) {
            try {
                // Variacion aleatoria +/-8% del valor actual
                double variacion = (Math.random() - 0.5) * 0.16 * sensor.getValorActual();
                double nuevoValor = Math.round((sensor.getValorActual() + variacion) * 10.0) / 10.0;

                // registrarLectura incluye: fueraDeRango, update sensor, alerta, email
                LecturaSensor guardada = sensorService.registrarLectura(sensor.getId(), nuevoValor);
                if (Boolean.TRUE.equals(guardada.getFueraDeRango())) {
                    alertasGeneradas++;
                }
            } catch (Exception e) {
                log.warn("[GreenCore] pollSensores: error procesando sensor {} - {}",
                        sensor.getCodigo(), e.getMessage());
            }
        }

        log.info("[GreenCore] pollSensores: completado. {} alertas generadas.", alertasGeneradas);
    }

    // =========================================================================
    // Tarea 2 - Reporte diario a las 7:00 am
    // =========================================================================

    /**
     * Genera y envia por correo Gmail el resumen diario del estado del invernadero.
     *
     * Solo envia el correo si hay alertas pendientes sin leer y el adminEmail
     * esta configurado en spring.mail.username.
     *
     * Cron: diario a las 7:00 am - "0 0 7 * * *"
     */
    @Scheduled(cron = "0 0 7 * * *")
    public void reporteDiario() {
        log.info("[GreenCore] reporteDiario: generando reporte diario...");

        long alertasPendientes = alertaService.findNoLeidas().size();
        String fecha = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy"));

        log.info("[GreenCore] reporteDiario: {} alertas sin leer al {}", alertasPendientes, fecha);

        if (alertasPendientes == 0) {
            log.info("[GreenCore] reporteDiario: sin alertas pendientes, no se envia correo.");
            return;
        }

        if (adminEmail == null || adminEmail.isBlank()) {
            log.warn("[GreenCore] reporteDiario: adminEmail no configurado, omitiendo correo.");
            return;
        }

        String subject = "[GreenCore] Reporte diario " + fecha
                + " - " + alertasPendientes + " alerta(s) pendiente(s)";

        String body = "REPORTE DIARIO GREENCORE\n"
                + "============================\n"
                + "Fecha: " + fecha + "\n\n"
                + "Alertas sin leer: " + alertasPendientes + "\n\n"
                + "Accede al dashboard para revisar el estado del invernadero:\n"
                + frontendUrl + "\n\n"
                + "--\n"
                + "Este es un mensaje automatico generado por GreenCore v1.0.0";

        emailService.sendNotification(adminEmail, subject, body);
        log.info("[GreenCore] reporteDiario: correo enviado a {}", adminEmail);
    }
}
