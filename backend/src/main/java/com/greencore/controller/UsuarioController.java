/**
 * GreenCore — Sistema de gestión de invernadero
 * Controlador REST para la entidad Usuario.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.controller;

import com.greencore.model.Usuario;
import com.greencore.service.UsuarioService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Expone los endpoints de consulta y administración de usuarios del sistema.
 * Los usuarios se crean automáticamente al autenticarse con Google OAuth2.
 * Solo el rol ADMIN puede cambiar roles o desactivar usuarios.
 * Base URL: {@code /api/v1/usuarios}
 */
@Tag(name = "Usuarios", description = "Administración de usuarios autenticados vía Google OAuth2")
@RestController
@RequestMapping("/api/v1/usuarios")
public class UsuarioController {

    private final UsuarioService service;

    /** @param service servicio de lógica de negocio para Usuario */
    public UsuarioController(UsuarioService service) {
        this.service = service;
    }

    /**
     * Retorna todos los usuarios registrados en el sistema.
     *
     * @return lista de usuarios con HTTP 200
     */
    @Operation(summary = "Listar usuarios", description = "Retorna todos los usuarios del sistema")
    @ApiResponse(responseCode = "200", description = "Lista de usuarios obtenida exitosamente")
    @GetMapping
    public ResponseEntity<List<Usuario>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    /**
     * Busca un usuario por su identificador único.
     *
     * @param id identificador del usuario
     * @return usuario encontrado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Obtener usuario por ID", description = "Busca un usuario por su identificador")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Usuario encontrado"),
        @ApiResponse(responseCode = "404", description = "Usuario no encontrado")
    })
    @GetMapping("/{id}")
    public ResponseEntity<Usuario> getById(
            @Parameter(description = "ID del usuario") @PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Crea manualmente un usuario. En operación normal los usuarios se crean
     * automáticamente al completar el flujo OAuth2 con Google.
     *
     * @param entity datos del usuario a crear
     * @return usuario creado con HTTP 201
     */
    @Operation(summary = "Crear usuario", description = "Crea un usuario manualmente (normalmente se crea vía OAuth2)")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "Usuario creado exitosamente"),
        @ApiResponse(responseCode = "409", description = "Email o providerId ya registrado")
    })
    @PostMapping
    public ResponseEntity<Usuario> create(@RequestBody Usuario entity) {
        Usuario saved = service.save(entity);
        return ResponseEntity.status(201).body(saved);
    }

    /**
     * Actualiza los datos de un usuario existente (rol, estado activo, etc.).
     *
     * @param id     identificador del usuario a actualizar
     * @param entity nuevos datos del usuario
     * @return usuario actualizado con HTTP 200, o HTTP 404 si no existe
     */
    @Operation(summary = "Actualizar usuario", description = "Modifica los datos de un usuario (rol, estado, etc.)")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "Usuario actualizado exitosamente"),
        @ApiResponse(responseCode = "404", description = "Usuario no encontrado")
    })
    @PutMapping("/{id}")
    public ResponseEntity<Usuario> update(
            @Parameter(description = "ID del usuario") @PathVariable Long id,
            @RequestBody Usuario entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Elimina un usuario del sistema.
     *
     * @param id identificador del usuario a eliminar
     * @return HTTP 204 sin contenido
     */
    @Operation(summary = "Eliminar usuario", description = "Elimina un usuario del sistema")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "Usuario eliminado exitosamente"),
        @ApiResponse(responseCode = "404", description = "Usuario no encontrado")
    })
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @Parameter(description = "ID del usuario") @PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
