/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad LecturaSensor.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.LecturaSensor;
import com.greencore.service.LecturaSensorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints para consultar el historial de lecturas de sensores.
 * Las lecturas se generan automáticamente cada 5 minutos vía cron, pero
 * también pueden registrarse manualmente a través de este endpoint.
 * Base URL: {@code /api/v1/lecturas_sensor}
 */
@Tag(name = "Lecturas de Sensor", description = "Historial de lecturas registradas por los sensores")
@RestController
@RequestMapping("/api/v1/lecturas_sensor")
public class LecturaSensorController {

    private final LecturaSensorService service;

    /** @param service servicio de lógica de negocio para LecturaSensor */
    public LecturaSensorController(LecturaSensorService service) {
        this.service = service;
    }

    /**
     * Retorna el historial completo de lecturas de todos los sensores.
     *
     * @return lista de lecturas con HTTP 200
     */
    @Operation(summary = "Listar lecturas", description = "Retorna el historial completo de lecturas de sensores")
    @ApiResponse(responseCode = "200", description = "Historial de lecturas obtenido exitosamente")
    @GetMapping
    public ResponseEntity<List<LecturaSensor>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Busca una lectura por su identificador único.
     *
     * @param id identificador de la lectura
     * @return lectura encontrada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener lectura por ID", description = "Busca una lectura por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Lectura encontrada"),
        @ApiResponse(responseCode = "404", description = "Lectura no encontrada")
    })
    @GetMapping("/{id}")
    public ResponseEntity<LecturaSensor> getById(
            @Parameter(description = "ID de la lectura") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra manualmente una lectura de sensor.
     * El campo {@code fueraDeRango} se calcula automáticamente comparando
     * el valor con los umbrales del sensor asociado.
     *
     * @param entity datos de la lectura a registrar
     * @return lectura creada con HTTP 201
     */
    @Operation(summary = "Crear lectura", description = "Registra una lectura manual; fueraDeRango se calcula automáticamente")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Lectura registrada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos inválidos o sensor inexistente")
    })
    @PostMapping
    public ResponseEntity<LecturaSensor> create(@RequestBody LecturaSensor entity) {
        LecturaSensor saved = service.save(entity);
        return ResponseEntity.status(201).body(saved);
    }

    /**
     * Actualiza los datos de una lectura existente.
     *
     * @param id     identificador de la lectura a actualizar
     * @param entity nuevos datos de la lectura
     * @return lectura actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar lectura", description = "Modifica los datos de una lectura existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Lectura actualizada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Lectura no encontrada")
    })
    @PutMapping("/{id}")
    public ResponseEntity<LecturaSensor> update(
            @Parameter(description = "ID de la lectura") @PathVariable Long id,
            @RequestBody LecturaSensor entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina una lectura del historial.
     *
     * @param id identificador de la lectura a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar lectura", description = "Elimina una lectura del historial")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Lectura eliminada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Lectura no encontrada")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la lectura") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
