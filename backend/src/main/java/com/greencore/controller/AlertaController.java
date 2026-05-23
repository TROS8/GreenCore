package com.greencore.controller;

import com.greencore.model.Alerta;
import com.greencore.service.AlertaService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/alertas")
public class AlertaController {

    private final AlertaService service;

    public AlertaController(AlertaService service) {
        this.service = service;
    }

    @GetMapping
    public ResponseEntity<List<Alerta>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/no-leidas")
    public ResponseEntity<List<Alerta>> getNoLeidas() {
        return ResponseEntity.ok(service.findNoLeidas());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Alerta> getById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Alerta> create(@RequestBody Alerta entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    @PatchMapping("/{id}/leer")
    public ResponseEntity<Alerta> marcarLeida(@PathVariable Long id) {
        return service.marcarLeida(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<Alerta> update(@PathVariable Long id, @RequestBody Alerta entity) {
        return service.findById(id)
                .map(existing -> {
                    entity.setId(id);
                    return ResponseEntity.ok(service.save(entity));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
