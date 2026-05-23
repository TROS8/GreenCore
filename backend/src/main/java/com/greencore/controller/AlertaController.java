/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Alerta.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Alerta;
import com.greencore.service.AlertaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints para consulta y gestión de alertas generadas automáticamente.
 * Las alertas CRITICO disparan notificación por correo Gmail al momento de crearse.
 * Base URL: {@code /api/v1/alertas}
 */
@Tag(name = "Alertas", description = "Consulta y gestión de alertas automáticas del invernadero")
@RestController
@RequestMapping("/api/v1/alertas")
public class AlertaController {

    private final AlertaService service;

    /** @param service servicio de lógica de negocio para Alerta */
    public AlertaController(AlertaService service) {
        this.service = service;
    }

    /**
     * Retorna todas las alertas registradas en el sistema.
     *
     * @return lista completa de alertas con HTTP 200
     */
    @Operation(summary = "Listar alertas", description = "Retorna todas las alertas del sistema")
    @ApiResponse(responseCode = "200", description = "Lista de alertas obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Alerta>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Retorna solo las alertas que aún no han sido marcadas como leídas.
     *
     * @return lista de alertas no leídas con HTTP 200
     */
    @Operation(summary = "Listar alertas no leídas", description = "Retorna alertas pendientes de revisión")
    @ApiResponse(responseCode = "200", description = "Alertas no leídas obtenidas exitosamente")
    @GetMapping("/no-leidas")
    public ResponseEntity<List<Alerta>> getNoLeidas() {
        return ResponseEntity.ok(service.findNoLeidas());
    }

    /**
     * Busca una alerta por su identificador único.
     *
     * @param id identificador de la alerta
     * @return alerta encontrada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener alerta por ID", description = "Busca una alerta por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Alerta encontrada"),
        @ApiResponse(responseCode = "404", description = "Alerta no encontrada")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Alerta> getById(
            @Parameter(description = "ID de la alerta") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Crea manualmente una alerta. En operación normal las alertas se generan
     * automáticamente al registrar lecturas fuera de rango.
     *
     * @param entity datos de la alerta a crear
     * @return alerta creada con HTTP 201
     */
    @Operation(summary = "Crear alerta", description = "Crea una alerta manualmente (normalmente son automáticas)")
    @ApiResponse(responseCode = "201", description = "Alerta creada exitosamente")
    @PostMapping
    public ResponseEntity<Alerta> create(@RequestBody Alerta entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    /**
     * Marca una alerta como leída por un usuario del sistema.
     *
     * @param id identificador de la alerta a marcar
     * @return alerta actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Marcar alerta como leída", description = "Cambia el estado leída=true de una alerta")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Alerta marcada como leída"),
        @ApiResponse(responseCode = "404", description = "Alerta no encontrada")
    })
    @PatchMapping("/{id}/leer")
    public ResponseEntity<Alerta> marcarLeida(
            @Parameter(description = "ID de la alerta") @PathVariable Long id) {
        return service.marcarLeida(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Actualiza una alerta existente.
     *
     * @param id     identificador de la alerta a actualizar
     * @param entity nuevos datos de la alerta
     * @return alerta actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar alerta", description = "Modifica los datos de una alerta existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Alerta actualizada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Alerta no encontrada")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Alerta> update(
            @Parameter(description = "ID de la alerta") @PathVariable Long id,
            @RequestBody Alerta entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina una alerta del historial.
     *
     * @param id identificador de la alerta a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar alerta", description = "Elimina una alerta del historial")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Alerta eliminada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Alerta no encontrada")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la alerta") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
