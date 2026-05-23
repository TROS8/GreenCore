/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para la entidad Planta. Gestiona el ciclo de vida y trazabilidad por lote.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.Planta;
import com.greencore.repository.PlantaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class PlantaService {

    private final PlantaRepository repository;

    public PlantaService(PlantaRepository repository) {
        this.repository = repository;
    }

    public List<Planta> findAll() {
        return repository.findAll();
    }

    public List<Planta> findByZonaId(Long zonaId) {
        return repository.findByZonaId(zonaId);
    }

    public Optional<Planta> findById(Long id) {
        return repository.findById(id);
    }

    public Planta save(Planta entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}
