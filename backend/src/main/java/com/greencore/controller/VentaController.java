/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Venta.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Venta;
import com.greencore.service.VentaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Expone los endpoints para registro y consulta de ventas de plantas.
 * Al crear una venta se descuenta el stock automáticamente.
 * Al anular una venta el stock se restaura.
 * El número de factura se genera con el patrón {@code FAC-{AÑO}-{SEQ}}.
 * Base URL: {@code /api/v1/ventas}
 */
@Tag(name = "Ventas", description = "Registro y consulta de ventas de plantas a clientes")
@RestController
@RequestMapping("/api/v1/ventas")
public class VentaController {

    private final VentaService service;

    /** @param service servicio de lógica de negocio para Venta */
    public VentaController(VentaService service) {
        this.service = service;
    }

    /**
     * Retorna todas las ventas, con filtrado opcional por rango de fechas.
     *
     * @param from fecha/hora de inicio del rango (ISO 8601, opcional)
     * @param to   fecha/hora de fin del rango (ISO 8601, opcional)
     * @return lista de ventas con HTTP 200
     */
    @Operation(
        summary = "Listar ventas",
        description = "Retorna todas las ventas. Acepta filtros opcionales ?from=&to= en formato ISO 8601"
    )
    @ApiResponse(responseCode = "200", description = "Lista de ventas obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Venta>> getAll(
            @Parameter(description = "Fecha inicio (ISO 8601)") @RequestParam(required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime from,
            @Parameter(description = "Fecha fin (ISO 8601)") @RequestParam(required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime to) {
        if (from != null && to != null) {
            return ResponseEntity.ok(service.findByFechaBetween(from, to));
        }
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Retorna todas las ventas realizadas por un cliente específico.
     *
     * @param clienteId identificador del cliente
     * @return lista de ventas del cliente con HTTP 200
     */
    @Operation(summary = "Ventas por cliente", description = "Filtra ventas por el identificador del cliente")
    @ApiResponse(responseCode = "200", description = "Ventas del cliente obtenidas exitosamente")
    @GetMapping("/cliente/{clienteId}")
    public ResponseEntity<List<Venta>> getByCliente(
            @Parameter(description = "ID del cliente") @PathVariable Long clienteId) {
        return ResponseEntity.ok(service.findByClienteId(clienteId));
    }

    /**
     * Busca una venta por su identificador único.
     *
     * @param id identificador de la venta
     * @return venta encontrada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener venta por ID", description = "Busca una venta por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Venta encontrada"),
        @ApiResponse(responseCode = "404", description = "Venta no encontrada")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Venta> getById(
            @Parameter(description = "ID de la venta") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra una nueva venta. Descuenta el stock de la planta automáticamente.
     * Falla con HTTP 400 si el stock disponible es insuficiente.
     *
     * @param entity datos de la venta a registrar
     * @return venta creada con HTTP 201
     */
    @Operation(
        summary = "Crear venta",
        description = "Registra una nueva venta y descuenta stock. Falla si stock insuficiente."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Venta creada y stock descontado exitosamente"),
        @ApiResponse(responseCode = "400", description = "Stock insuficiente o datos inválidos")
    })
    @PostMapping
    public ResponseEntity<Venta> create(@RequestBody Venta entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    /**
     * Actualiza una venta existente. Si se cambia el estado a ANULADA,
     * el stock de la planta se restaura automáticamente.
     *
     * @param id     identificador de la venta a actualizar
     * @param entity nuevos datos de la venta
     * @return venta actualizada con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(
        summary = "Actualizar venta",
        description = "Modifica una venta. Si estado cambia a ANULADA, restaura el stock."
    )
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Venta actualizada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Venta no encontrada")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Venta> update(
            @Parameter(description = "ID de la venta") @PathVariable Long id,
            @RequestBody Venta entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina una venta del sistema.
     *
     * @param id identificador de la venta a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar venta", description = "Elimina una venta del sistema")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Venta eliminada exitosamente"),
        @ApiResponse(responseCode = "404", description = "Venta no encontrada")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID de la venta") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
