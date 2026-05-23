/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Cliente.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Cliente;
import com.greencore.service.ClienteService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints CRUD para clientes compradores del invernadero.
 * Un cliente con ventas registradas no puede ser eliminado del sistema.
 * Base URL: {@code /api/v1/clientes}
 */
@Tag(name = "Clientes", description = "Gestión de clientes compradores del invernadero")
@RestController
@RequestMapping("/api/v1/clientes")
public class ClienteController {

    private final ClienteService service;

    /** @param service servicio de lógica de negocio para Cliente */
    public ClienteController(ClienteService service) {
        this.service = service;
    }

    /**
     * Retorna todos los clientes registrados.
     *
     * @return lista de clientes con HTTP 200
     */
    @Operation(summary = "Listar clientes", description = "Retorna todos los clientes del sistema")
    @ApiResponse(responseCode = "200", description = "Lista de clientes obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Cliente>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Busca un cliente por su identificador único.
     *
     * @param id identificador del cliente
     * @return cliente encontrado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener cliente por ID", description = "Busca un cliente por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Cliente encontrado"),
        @ApiResponse(responseCode = "404", description = "Cliente no encontrado")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Cliente> getById(
            @Parameter(description = "ID del cliente") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Registra un nuevo cliente en el sistema.
     * El email debe ser único por cliente.
     *
     * @param entity datos del cliente a registrar
     * @return cliente creado con HTTP 201
     */
    @Operation(summary = "Crear cliente", description = "Registra un nuevo cliente; el email debe ser único")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Cliente creado exitosamente"),
        @ApiResponse(responseCode = "409", description = "Email ya registrado en otro cliente")
    })
    @PostMapping
    public ResponseEntity<Cliente> create(@RequestBody Cliente entity) {
        Cliente saved = service.save(entity);
        return ResponseEntity.status(201).body(saved);
    }

    /**
     * Actualiza los datos de un cliente existente.
     *
     * @param id     identificador del cliente a actualizar
     * @param entity nuevos datos del cliente
     * @return cliente actualizado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar cliente", description = "Modifica los datos de un cliente existente")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Cliente actualizado exitosamente"),
        @ApiResponse(responseCode = "404", description = "Cliente no encontrado")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Cliente> update(
            @Parameter(description = "ID del cliente") @PathVariable Long id,
            @RequestBody Cliente entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina un cliente del sistema.
     * Falla con HTTP 400 si el cliente tiene ventas asociadas.
     *
     * @param id identificador del cliente a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar cliente", description = "Elimina un cliente; falla si tiene ventas asociadas")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Cliente eliminado exitosamente"),
        @ApiResponse(responseCode = "400", description = "El cliente tiene ventas asociadas"),
        @ApiResponse(responseCode = "404", description = "Cliente no encontrado")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del cliente") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
