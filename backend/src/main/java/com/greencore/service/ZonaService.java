package com.greencore.service;

import com.greencore.model.Zona;
import com.greencore.repository.ZonaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ZonaService {

    private final ZonaRepository repository;

    public ZonaService(ZonaRepository repository) {
        this.repository = repository;
    }

    public List<Zona> findAll() {
        return repository.findAll();
    }

    public Optional<Zona> findById(Long id) {
        return repository.findById(id);
    }

    public Zona save(Zona entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}