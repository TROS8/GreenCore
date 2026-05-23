package com.greencore.service;

import com.greencore.model.Venta;
import com.greencore.repository.VentaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class VentaService {

    private final VentaRepository repository;

    public VentaService(VentaRepository repository) {
        this.repository = repository;
    }

    public List<Venta> findAll() {
        return repository.findAll();
    }

    public Optional<Venta> findById(Long id) {
        return repository.findById(id);
    }

    public Venta save(Venta entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}