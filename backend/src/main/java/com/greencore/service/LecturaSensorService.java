/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para LecturaSensor.
 * <p>
 * Al registrar una lectura:
 * <ul>
 *   <li>Calcula automaticamente {@code fueraDeRango} comparando el valor con los umbrales del sensor.</li>
 *   <li>Actualiza {@code valorActual} y {@code ultimaLectura} en el Sensor.</li>
 *   <li>Si el valor esta fuera de rango, genera una {@link com.greencore.model.Alerta} automaticamente.</li>
 *   <li>Si el sensor esta en estado FALLA, rechaza la lectura con HTTP 409.</li>
 * </ul>
 * </p>
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.Alerta;
import com.greencore.model.EstadoSensor;
import com.greencore.model.LecturaSensor;
import com.greencore.model.NivelAlerta;
import com.greencore.model.Sensor;
import com.greencore.repository.LecturaSensorRepository;
import com.greencore.repository.SensorRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class LecturaSensorService {

    private final LecturaSensorRepository repository;
    private final SensorRepository sensorRepository;
    private final AlertaService alertaService;

    /**
     * @param repository       repositorio JPA de lecturas
     * @param sensorRepository repositorio JPA de sensores (para actualizar valorActual)
     * @param alertaService    servicio de alertas (para crear alerta si fuera de rango)
     */
    public LecturaSensorService(LecturaSensorRepository repository,
                                SensorRepository sensorRepository,
                                AlertaService alertaService) {
        this.repository = repository;
        this.sensorRepository = sensorRepository;
        this.alertaService = alertaService;
    }

    /** Retorna el historial completo de lecturas. */
    public List<LecturaSensor> findAll() {
        return repository.findAll();
    }

    /** Busca una lectura por ID. */
    public Optional<LecturaSensor> findById(Long id) {
        return repository.findById(id);
    }

    /**
     * Registra una lectura de sensor aplicando logica de negocio completa:
     * <ol>
     *   <li>Recarga el Sensor desde BD para obtener umbrales actualizados.</li>
     *   <li>Rechaza si el sensor esta en FALLA (HTTP 409).</li>
     *   <li>Calcula {@code fueraDeRango}.</li>
     *   <li>Actualiza {@code valorActual} y {@code ultimaLectura} del Sensor.</li>
     *   <li>Si fuera de rango, crea una Alerta (CRITICO si supera max, ADVERTENCIA si baja de min).</li>
     * </ol>
     *
     * @param entity lectura a registrar (solo requiere {@code valor} y {@code sensor.id})
     * @return lectura persistida con {@code fueraDeRango} calculado
     * @throws ResponseStatusException HTTP 409 si el sensor esta en FALLA
     * @throws ResponseStatusException HTTP 404 si el sensor no existe
     */
    public LecturaSensor save(LecturaSensor entity) {
        // 1 ── Cargar el sensor completo desde BD
        Long sensorId = entity.getSensor() == null ? null : entity.getSensor().getId();
        Sensor sensor = sensorRepository.findById(sensorId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Sensor no encontrado con ID: " + sensorId));

        // 2 ── Rechazar lecturas si el sensor esta en FALLA
        if (EstadoSensor.FALLA.equals(sensor.getEstado())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT,
                    "El sensor " + sensor.getCodigo() + " esta en estado FALLA y no acepta lecturas");
        }

        // 3 ── Calcular fueraDeRango automaticamente
        double valor = entity.getValor();
        boolean fuera = valor < sensor.getUmbralMinimo() || valor > sensor.getUmbralMaximo();
        entity.setFueraDeRango(fuera);

        // 4 ── Establecer timestamp si no viene informado
        if (entity.getTimestamp() == null) {
            entity.setTimestamp(LocalDateTime.now());
        }

        // 5 ── Actualizar sensor: valorActual y ultimaLectura
        sensor.setValorActual(valor);
        sensor.setUltimaLectura(entity.getTimestamp());
        sensorRepository.save(sensor);

        // 6 ── Persistir la lectura
        LecturaSensor guardada = repository.save(entity);

        // 7 ── Si fuera de rango, crear alerta automatica
        if (fuera) {
            crearAlertaAutomatica(sensor, valor);
        }

        return guardada;
    }

    /**
     * Elimina una lectura del historial.
     *
     * @param id identificador de la lectura a eliminar
     */
    public void delete(Long id) {
        repository.deleteById(id);
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Metodos privados de negocio
    // ──────────────────────────────────────────────────────────────────────────

    /**
     * Crea una {@link Alerta} automatica cuando un sensor registra un valor fuera de rango.
     * El nivel es:
     * <ul>
     *   <li>{@code CRITICO}    si el valor supera el umbral maximo.</li>
     *   <li>{@code ADVERTENCIA} si el valor esta por debajo del umbral minimo.</li>
     * </ul>
     *
     * @param sensor sensor que genero la lectura fuera de rango
     * @param valor  valor registrado fuera de rango
     */
    private void crearAlertaAutomatica(Sensor sensor, double valor) {
        NivelAlerta nivel = (valor > sensor.getUmbralMaximo())
                ? NivelAlerta.CRITICO
                : NivelAlerta.ADVERTENCIA;

        String zona = sensor.getZona() != null ? sensor.getZona().getNombre() : "desconocida";
        String condicion = nivel == NivelAlerta.CRITICO
                ? "supero el umbral maximo (" + sensor.getUmbralMaximo() + ")"
                : "bajo del umbral minimo (" + sensor.getUmbralMinimo() + ")";

        String mensaje = String.format("Sensor %s [%s] en Zona %s: valor %.1f %s %s",
                sensor.getCodigo(), sensor.getTipo(), zona,
                valor, sensor.getUnidad(), condicion);

        Alerta alerta = new Alerta();
        alerta.setSensor(sensor);
        alerta.setMensaje(mensaje);
        alerta.setNivel(nivel);
        alerta.setValorRegistrado(valor);
        alerta.setTimestamp(LocalDateTime.now());
        alerta.setLeida(false);
        alerta.setCorreoEnviado(false);

        alertaService.save(alerta);   // AlertaService enviara email si nivel == CRITICO
    }
}