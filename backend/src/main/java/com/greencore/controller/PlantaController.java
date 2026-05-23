/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Planta.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Planta;
import com.greencore.service.PlantaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints CRUD para plantas cultivadas en el invernadero.
 * Incluye filtrado por zona para trazabilidad por lote.
 * Base URL: {@code /api/v1/plantas}
 */
@Tag(name = "Plantas", description = "Gestión de plantas cultivadas en el invernadero")
@RestController
@RequestMapping("/api/v1/plantas")
public class PlantaController {

    private final PlantaService service;

    /** @param service servicio de lógica de negocio para Planta */
    public PlantaController(PlantaService service) {
        this.service = service;
    }

    /**
     * Retorna todas las plantas registradas, con filtrado opcional por zona.
     *
     * @return lista completa de plantas con HTTP 200
     */
    @Operation(summary = "Listar plantas", description = "Retorna todas las plantas del inventario")
    @ApiResponse(responseCode = "200", description = "Lista de plantas obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Planta>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Retorna todas las plantas ubicadas en una zona específica.
     *
     * @param zonaId identificador de la zona
     * @return lista de plantas de esa zona con HTTP 200
     */
    @Operation(summary = "Listar plantas por zona", description = "Filtra plantas por zona del invernadero")
    @ApiResponse(responseCode = "200", description = "Plantas de la zona obtenidas exitosamente")
    @GetMapping("/zona/{zonaId}")
    public ResponseEntity<List<Planta>> getByZona(
            @Parameter(description = "ID de la zona") @PathVariable Long zonaId) {
        return ResponseEntity.ok(service.findByZonaId(zonaId));
    }

    /**
     * Busca una planta por su identificador único.
     *
     * @param id identificador de la planta
     * @return planta encontrada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener planta por ID", description = "Busca una planta por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Planta encontrada"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Planta> getById(
            @Parameter(description = "ID de la planta") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra una nueva planta en el inventario.
     * El lote se genera automáticamente con el patrón {@code LOT-{AÑO}-{SEQ}}.
     *
     * @param entity datos de la planta a registrar
     * @return planta creada con HTTP 201
     */
    @Operation(summary = "Crear planta", description = "Registra una nueva planta; el lote se genera automáticamente")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Planta creada exitosamente"),
        @ApiResponse(responseCode = "400", description = "Datos de entrada inválidos o zona inexistente")
    })
    @PostMapping
    public ResponseEntity<Planta> create(@RequestBody Planta entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    /**
     * Actualiza los datos de una planta existente.
     *
     * @param id     identificador de la planta a actualizar
     * @param entity nuevos datos de la planta
     * @return planta actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar planta", description = "Modifica los datos de una planta existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Planta actualizada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Planta> update(
            @Parameter(description = "ID de la planta") @PathVariable Long id,
            @RequestBody Planta entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina una planta del inventario.
     *
     * @param id identificador de la planta a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar planta", description = "Elimina una planta del inventario")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Planta eliminada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Planta no encontrada")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la planta") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
