/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para Alerta.
 * <p>
 * Al guardar una alerta de nivel {@code CRITICO}, envia automaticamente
 * una notificacion por correo Gmail al administrador configurado en
 * {@code spring.mail.username}.
 * </p>
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.Alerta;
import com.greencore.model.NivelAlerta;
import com.greencore.repository.AlertaRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class AlertaService {

    private final AlertaRepository repository;
    private final EmailNotificationService emailService;

    /** Correo destinatario de alertas criticas (configurado en spring.mail.username). */
    @Value("${spring.mail.username:}")
    private String adminEmail;

    /**
     * @param repository   repositorio JPA de alertas
     * @param emailService servicio de correo Gmail para notificaciones
     */
    public AlertaService(AlertaRepository repository, EmailNotificationService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }

    /** Retorna todas las alertas registradas. */
    public List<Alerta> findAll() {
        return repository.findAll();
    }

    /** Retorna las alertas que aun no han sido leidas. */
    public List<Alerta> findNoLeidas() {
        return repository.findByLeidaFalse();
    }

    /** Busca una alerta por ID. */
    public Optional<Alerta> findById(Long id) {
        return repository.findById(id);
    }

    /**
     * Marca una alerta como leida.
     *
     * @param id identificador de la alerta
     * @return alerta actualizada, o empty si no existe
     */
    public Optional<Alerta> marcarLeida(Long id) {
        return repository.findById(id).map(alerta -> {
            alerta.setLeida(true);
            return repository.save(alerta);
        });
    }

    /**
     * Persiste una alerta. Si el nivel es {@code CRITICO} y no se ha enviado correo aun,
     * envia una notificacion automatica por Gmail al administrador.
     *
     * @param entity alerta a persistir
     * @return alerta guardada (con {@code correoEnviado = true} si se envio el correo)
     */
    public Alerta save(Alerta entity) {
        Alerta guardada = repository.save(entity);

        // Enviar correo automatico en alertas CRITICAS
        if (NivelAlerta.CRITICO.equals(guardada.getNivel())
                && !Boolean.TRUE.equals(guardada.getCorreoEnviado())
                && adminEmail != null && !adminEmail.isBlank()) {

            String sensorCodigo = guardada.getSensor() != null
                    ? guardada.getSensor().getCodigo() : "desconocido";

            String subject = "[GreenCore] ALERTA CRITICA - Sensor " + sensorCodigo;
            String body = "*** ALERTA CRITICA en el invernadero ***\n\n"
                    + "Sensor: " + sensorCodigo + "\n"
                    + "Valor registrado: " + guardada.getValorRegistrado() + "\n"
                    + "Mensaje: " + guardada.getMensaje() + "\n"
                    + "Fecha: " + guardada.getTimestamp() + "\n\n"
                    + "Revisa el invernadero de inmediato.\n"
                    + "Dashboard: https://greencore-frontend.onrender.com";

            emailService.sendNotification(adminEmail, subject, body);

            guardada.setCorreoEnviado(true);
            guardada = repository.save(guardada);
        }

        return guardada;
    }

    /**
     * Elimina una alerta por ID.
     *
     * @param id identificador de la alerta a eliminar
     */
    public void delete(Long id) {
        repository.deleteById(id);
    }
}
