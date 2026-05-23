package com.greencore.service;

import com.greencore.model.Sensor;
import com.greencore.repository.SensorRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class SensorService {

    private final SensorRepository repository;

    public SensorService(SensorRepository repository) {
        this.repository = repository;
    }

    public List<Sensor> findAll() {
        return repository.findAll();
    }

    public Optional<Sensor> findById(Long id) {
        return repository.findById(id);
    }

    public Sensor save(Sensor entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}