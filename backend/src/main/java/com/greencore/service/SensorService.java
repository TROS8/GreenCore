/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para Sensor. Gestiona lecturas y dispara alertas automaticas.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.*;
import com.greencore.repository.LecturaSensorRepository;
import com.greencore.repository.SensorRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Servicio de logica de negocio para Sensor.
 * <p>
 * El metodo {@link #registrarLectura} es el punto de entrada principal para
 * la ingesta de valores. Ademas de persistir la lectura y actualizar el sensor,
 * crea alertas automaticas via {@link AlertaService} (que a su vez envia correo
 * Gmail si el nivel es CRITICO).
 * </p>
 */
@Service
@Transactional
public class SensorService {

    private final SensorRepository sensorRepository;
    private final LecturaSensorRepository lecturaRepository;
    private final AlertaService alertaService;

    /**
     * @param sensorRepository  repositorio JPA de sensores
     * @param lecturaRepository repositorio JPA de lecturas
     * @param alertaService     servicio de alertas (incluye envio de correo Gmail en CRITICO)
     */
    public SensorService(SensorRepository sensorRepository,
                         LecturaSensorRepository lecturaRepository,
                         AlertaService alertaService) {
        this.sensorRepository = sensorRepository;
        this.lecturaRepository = lecturaRepository;
        this.alertaService = alertaService;
    }

    /** Retorna todos los sensores registrados. */
    public List<Sensor> findAll() {
        return sensorRepository.findAll();
    }

    /** Busca un sensor por ID. */
    public Optional<Sensor> findById(Long id) {
        return sensorRepository.findById(id);
    }

    /** Persiste o actualiza un sensor. */
    public Sensor save(Sensor entity) {
        return sensorRepository.save(entity);
    }

    /** Elimina un sensor por ID. */
    public void delete(Long id) {
        sensorRepository.deleteById(id);
    }

    /**
     * Registra una lectura de valor para un sensor aplicando logica completa:
     * <ol>
     *   <li>Rechaza si el sensor esta en FALLA (HTTP 409).</li>
     *   <li>Calcula {@code fueraDeRango} contra los umbrales del sensor.</li>
     *   <li>Actualiza {@code valorActual} y {@code ultimaLectura} del sensor.</li>
     *   <li>Si fuera de rango, crea una {@link Alerta} via {@link AlertaService#save}
     *       (que envia correo Gmail automaticamente en nivel CRITICO).</li>
     * </ol>
     * <p>
     * Nivel de alerta:
     * <ul>
     *   <li>{@code CRITICO}    — valor supera umbral maximo.</li>
     *   <li>{@code ADVERTENCIA} — valor cae por debajo del umbral minimo.</li>
     * </ul>
     * </p>
     *
     * @param sensorId ID del sensor
     * @param valor    valor medido por el sensor
     * @return lectura persistida con {@code fueraDeRango} calculado
     * @throws ResponseStatusException HTTP 404 si el sensor no existe
     * @throws ResponseStatusException HTTP 409 si el sensor esta en FALLA
     */
    public LecturaSensor registrarLectura(Long sensorId, Double valor) {
        // 1 ── Cargar sensor
        Sensor sensor = sensorRepository.findById(sensorId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Sensor no encontrado: " + sensorId));

        // 2 ── Rechazar si sensor en FALLA
        if (EstadoSensor.FALLA.equals(sensor.getEstado())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT,
                    "El sensor " + sensor.getCodigo() + " esta en estado FALLA y no acepta lecturas");
        }

        // 3 ── Calcular fueraDeRango
        boolean fueraDeRango = valor < sensor.getUmbralMinimo() || valor > sensor.getUmbralMaximo();

        // 4 ── Persistir lectura
        LecturaSensor lectura = new LecturaSensor();
        lectura.setValor(valor);
        lectura.setFueraDeRango(fueraDeRango);
        lectura.setTimestamp(LocalDateTime.now());
        lectura.setSensor(sensor);
        lecturaRepository.save(lectura);

        // 5 ── Actualizar sensor: valorActual y ultimaLectura
        sensor.setValorActual(valor);
        sensor.setUltimaLectura(LocalDateTime.now());
        sensorRepository.save(sensor);

        // 6 ── Crear alerta automatica si fuera de rango
        if (fueraDeRango) {
            NivelAlerta nivel = (valor > sensor.getUmbralMaximo())
                    ? NivelAlerta.CRITICO
                    : NivelAlerta.ADVERTENCIA;

            String dir = nivel == NivelAlerta.CRITICO
                    ? "supero umbral maximo (" + sensor.getUmbralMaximo() + ")"
                    : "bajo del umbral minimo (" + sensor.getUmbralMinimo() + ")";

            String msg = String.format("Sensor %s [%s]: valor %.2f %s %s",
                    sensor.getCodigo(), sensor.getTipo(), valor, sensor.getUnidad(), dir);

            Alerta alerta = new Alerta();
            alerta.setMensaje(msg);
            alerta.setNivel(nivel);
            alerta.setLeida(false);
            alerta.setCorreoEnviado(false);
            alerta.setValorRegistrado(valor);
            alerta.setTimestamp(LocalDateTime.now());
            alerta.setSensor(sensor);

            alertaService.save(alerta);   // envia correo Gmail si CRITICO
        }

        return lectura;
    }
}
