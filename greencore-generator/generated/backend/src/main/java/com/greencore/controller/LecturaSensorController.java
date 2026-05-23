package com.greencore.controller;

import com.greencore.model.LecturaSensor;
import com.greencore.service.LecturaSensorService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/lecturas_sensor")
public class LecturaSensorController {

    private final LecturaSensorService service;

    public LecturaSensorController(LecturaSensorService service) {
        this.service = service;
    }

    @GetMapping
    public ResponseEntity<List<LecturaSensor>> getAll() {
        return ResponseEntity.ok(service.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<LecturaSensor> getById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<LecturaSensor> create(@RequestBody LecturaSensor entity) {
        LecturaSensor saved = service.save(entity);
        return ResponseEntity.status(201).body(saved);
    }

    @PutMapping("/{id}")
    public ResponseEntity<LecturaSensor> update(@PathVariable Long id, @RequestBody LecturaSensor entity) {
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