/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de envio de notificaciones por correo Gmail via Spring Mail.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailNotificationService {

    private final JavaMailSender mailSender;

    public EmailNotificationService(@Autowired(required = false) JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void sendNotification(String to, String subject, String body) {
        if (mailSender == null) return;
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(body);
        mailSender.send(message);
    }
}
