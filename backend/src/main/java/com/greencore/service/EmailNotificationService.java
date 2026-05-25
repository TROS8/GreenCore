/**
 * GreenCore - Sistema de gestion de invernadero
 * Servicio de envio de notificaciones por correo Gmail via Spring Mail.
 * <p>
 * Si el servidor SMTP no esta disponible (p. ej. en entorno de test),
 * la excepcion se captura y se registra en el log sin interrumpir la
 * logica de negocio del llamador.
 * </p>
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.MailException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailNotificationService {

    private static final Logger log = LoggerFactory.getLogger(EmailNotificationService.class);

    private final JavaMailSender mailSender;

    public EmailNotificationService(@Autowired(required = false) JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    /**
     * Envia una notificacion por correo electronico.
     * Si el servidor SMTP no esta disponible o el envio falla, registra el error
     * en el log y retorna sin lanzar excepcion (el flujo de negocio no se interrumpe).
     *
     * @param to      direccion de correo destinataria
     * @param subject asunto del mensaje
     * @param body    cuerpo del mensaje en texto plano
     */
    public void sendNotification(String to, String subject, String body) {
        if (mailSender == null) {
            log.debug("[GreenCore] EmailService: JavaMailSender no disponible, correo omitido.");
            return;
        }
        if (to == null || to.isBlank()) {
            log.debug("[GreenCore] EmailService: destinatario vacio, correo omitido.");
            return;
        }
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setTo(to);
            message.setSubject(subject);
            message.setText(body);
            mailSender.send(message);
            log.info("[GreenCore] EmailService: correo enviado a {}", to);
        } catch (MailException e) {
            log.warn("[GreenCore] EmailService: no se pudo enviar correo a {} - {}", to, e.getMessage());
        } catch (Exception e) {
            log.warn("[GreenCore] EmailService: error inesperado al enviar correo - {}", e.getMessage());
        }
    }
}
