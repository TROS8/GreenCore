/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Zona.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Zona;
import com.greencore.service.ZonaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints CRUD para zonas físicas del invernadero.
 * Base URL: {@code /api/v1/zonas}
 */
@Tag(name = "Zonas", description = "Gestión de zonas físicas del invernadero")
@RestController
@RequestMapping("/api/v1/zonas")
public class ZonaController {

    private final ZonaService service;

    /** @param service servicio de lógica de negocio para Zona */
    public ZonaController(ZonaService service) {
        this.service = service;
    }

    /**
     * Retorna todas las zonas registradas.
     *
     * @return lista de zonas con HTTP 200
     */
    @Operation(summary = "Listar zonas", description = "Retorna todas las zonas del invernadero")
    @ApiResponse(responseCode = "200", description = "Lista de zonas obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Zona>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Busca una zona por su identificador único.
     *
     * @param id identificador de la zona
     * @return zona encontrada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener zona por ID", description = "Busca una zona por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Zona encontrada"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Zona> getById(
            @Parameter(description = "ID de la zona") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Crea una nueva zona en el invernadero.
     *
     * @param entity datos de la zona a crear
     * @return zona creada con HTTP 201
     */
    @Operation(summary = "Crear zona", description = "Registra una nueva zona física en el invernadero")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Zona creada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos de entrada inválidos")
    })
    @PostMapping
    public ResponseEntity<Zona> create(@RequestBody Zona entity) {
        Zona saved = service.save(entity);
        return ResponseEntity.status(201).body(saved);
    }

    /**
     * Actualiza los datos de una zona existente.
     *
     * @param id     identificador de la zona a actualizar
     * @param entity nuevos datos de la zona
     * @return zona actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar zona", description = "Modifica los datos de una zona existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Zona actualizada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Zona> update(
            @Parameter(description = "ID de la zona") @PathVariable Long id,
            @RequestBody Zona entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina una zona por su identificador.
     *
     * @param id identificador de la zona a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar zona", description = "Elimina una zona del sistema")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Zona eliminada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Zona no encontrada")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la zona") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
