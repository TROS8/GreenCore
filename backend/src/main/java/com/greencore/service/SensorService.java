/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para Sensor. Gestiona lecturas y dispara alertas automaticas.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.*;
import com.greencore.repository.AlertaRepository;
import com.greencore.repository.LecturaSensorRepository;
import com.greencore.repository.SensorRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class SensorService {

    private final SensorRepository sensorRepository;
    private final LecturaSensorRepository lecturaRepository;
    private final AlertaRepository alertaRepository;

    public SensorService(SensorRepository sensorRepository,
                         LecturaSensorRepository lecturaRepository,
                         AlertaRepository alertaRepository) {
        this.sensorRepository = sensorRepository;
        this.lecturaRepository = lecturaRepository;
        this.alertaRepository = alertaRepository;
    }

    public List<Sensor> findAll() {
        return sensorRepository.findAll();
    }

    public Optional<Sensor> findById(Long id) {
        return sensorRepository.findById(id);
    }

    public Sensor save(Sensor entity) {
        return sensorRepository.save(entity);
    }

    public void delete(Long id) {
        sensorRepository.deleteById(id);
    }

    public LecturaSensor registrarLectura(Long sensorId, Double valor) {
        Sensor sensor = sensorRepository.findById(sensorId)
                .orElseThrow(() -> new RuntimeException("Sensor no encontrado: " + sensorId));

        boolean fueraDeRango = valor < sensor.getUmbralMinimo() || valor > sensor.getUmbralMaximo();

        LecturaSensor lectura = new LecturaSensor();
        lectura.setValor(valor);
        lectura.setFueraDeRango(fueraDeRango);
        lectura.setTimestamp(LocalDateTime.now());
        lectura.setSensor(sensor);
        lecturaRepository.save(lectura);

        sensor.setValorActual(valor);
        sensor.setUltimaLectura(LocalDateTime.now());
        sensorRepository.save(sensor);

        if (fueraDeRango) {
            double rango = sensor.getUmbralMaximo() - sensor.getUmbralMinimo();
            double desviacion = Math.max(
                    valor - sensor.getUmbralMaximo(),
                    sensor.getUmbralMinimo() - valor
            );
            NivelAlerta nivel = desviacion > rango * 0.1 ? NivelAlerta.CRITICO : NivelAlerta.ADVERTENCIA;
            String dir = valor > sensor.getUmbralMaximo() ? "superó umbral máximo" : "cayó bajo umbral mínimo";
            String msg = String.format("Sensor %s %s (%.2f; rango %.2f–%.2f)",
                    sensor.getCodigo(), dir, valor, sensor.getUmbralMinimo(), sensor.getUmbralMaximo());

            Alerta alerta = new Alerta();
            alerta.setMensaje(msg);
            alerta.setNivel(nivel);
            alerta.setLeida(false);
            alerta.setCorreoEnviado(false);
            alerta.setValorRegistrado(valor);
            alerta.setTimestamp(LocalDateTime.now());
            alerta.setSensor(sensor);
            alertaRepository.save(alerta);
        }

        return lectura;
    }
}
