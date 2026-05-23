/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para LecturaSensor. Registra el historial de lecturas.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.LecturaSensor;
import com.greencore.repository.LecturaSensorRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class LecturaSensorService {

    private final LecturaSensorRepository repository;

    public LecturaSensorService(LecturaSensorRepository repository) {
        this.repository = repository;
    }

    public List<LecturaSensor> findAll() {
        return repository.findAll();
    }

    public Optional<LecturaSensor> findById(Long id) {
        return repository.findById(id);
    }

    public LecturaSensor save(LecturaSensor entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}