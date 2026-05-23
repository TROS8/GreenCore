package com.greencore.controller;

import com.greencore.model.Planta;
import com.greencore.service.PlantaService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/plantas")
public class PlantaController {

    private final PlantaService service;

    public PlantaController(PlantaService service) {
        this.service = service;
    }

    @GetMapping
    public ResponseEntity<List<Planta>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/zona/{zonaId}")
    public ResponseEntity<List<Planta>> getByZona(@PathVariable Long zonaId) {
        return ResponseEntity.ok(service.findByZonaId(zonaId));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Planta> getById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Planta> create(@RequestBody Planta entity) {
        return ResponseEntity.status(201).body(service.save(entity));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Planta> update(@PathVariable Long id, @RequestBody Planta entity) {
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
