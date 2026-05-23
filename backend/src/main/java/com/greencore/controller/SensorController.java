/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Sensor.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.LecturaSensor;
import com.greencore.model.Sensor;
import com.greencore.service.SensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * Expone los endpoints CRUD para sensores físicos del invernadero.
 * Incluye el endpoint de registro de lectura que dispara alertas automáticas.
 * Base URL: {@code /api/v1/sensores}
 */
@Tag(name = "Sensores", description = "Gestión de sensores físicos e ingesta de lecturas")
@RestController
@RequestMapping("/api/v1/sensores")
public class SensorController {

    private final SensorService service;

    /** @param service servicio de lógica de negocio para Sensor */
    public SensorController(SensorService service) {
        this.service = service;
    }

    /**
     * Retorna todos los sensores registrados en el sistema.
     *
     * @return lista de sensores con HTTP 200
     */
    @Operation(summary = "Listar sensores", description = "Retorna todos los sensores del invernadero")
    @ApiResponse(responseCode = "200", description = "Lista de sensores obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Sensor>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Busca un sensor por su identificador único.
     *
     * @param id identificador del sensor
     * @return sensor encontrado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener sensor por ID", description = "Busca un sensor por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Sensor encontrado"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Sensor> getById(
            @Parameter(description = "ID del sensor") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra un nuevo sensor en el sistema.
     *
     * @param entity datos del sensor a crear
     * @return sensor creado con HTTP 201
     */
    @Operation(summary = "Crear sensor", description = "Registra un nuevo sensor físico en el invernadero")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Sensor creado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos o zona inexistente")
    })
    @PostMapping
    public ResponseEntity<Sensor> create(@RequestBody Sensor entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    /**
     * Actualiza los datos de un sensor existente.
     *
     * @param id     identificador del sensor a actualizar
     * @param entity nuevos datos del sensor
     * @return sensor actualizado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar sensor", description = "Modifica los datos de un sensor existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Sensor actualizado exitosamente"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Sensor> update(
            @Parameter(description = "ID del sensor") @PathVariable Long id,
            @RequestBody Sensor entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra una lectura de valor para un sensor.
     * Si el valor supera los umbrales configurados, se genera una alerta automáticamente.
     *
     * @param id   identificador del sensor
     * @param body mapa con la clave {@code "valor"} (numérico)
     * @return lectura registrada con HTTP 201, o HTTP 400 si falta el valor
     */
    @Operation(
        summary = "Registrar lectura",
        description = "Ingesta un valor de lectura para el sensor. Genera alerta si supera umbrales."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Lectura registrada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Campo 'valor' ausente o sensor en estado FALLA"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    @PostMapping("/{id}/lectura")
    public ResponseEntity<LecturaSensor> registrarLectura(
            @Parameter(description = "ID del sensor") @PathVariable Long id,
            @RequestBody Map<String, Object> body) {
        Object raw = body.get("valor");
        if (raw == null) return ResponseEntity.badRequest().build();
        double valor = ((Number) raw).doubleValue();
        return ResponseEntity.status(201).body(service.registrarLectura(id, valor));
    }

    /**
     * Elimina un sensor del sistema.
     *
     * @param id identificador del sensor a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar sensor", description = "Elimina un sensor del sistema")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Sensor eliminado exitosamente"),
        @ApiResponse(responseCode = "404", description = "Sensor no encontrado")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del sensor") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
