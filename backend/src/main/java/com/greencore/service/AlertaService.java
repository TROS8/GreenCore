package com.greencore.service;

import com.greencore.model.Alerta;
import com.greencore.repository.AlertaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class AlertaService {

    private final AlertaRepository repository;

    public AlertaService(AlertaRepository repository) {
        this.repository = repository;
    }

    public List<Alerta> findAll() {
        return repository.findAll();
    }

    public List<Alerta> findNoLeidas() {
        return repository.findByLeidaFalse();
    }

    public Optional<Alerta> findById(Long id) {
        return repository.findById(id);
    }

    public Optional<Alerta> marcarLeida(Long id) {
        return repository.findById(id).map(alerta -> {
            alerta.setLeida(true);
            return repository.save(alerta);
        });
    }

    public Alerta save(Alerta entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}
