/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para Venta. Gestiona stock y facturacion automatica.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.Venta;
import com.greencore.repository.VentaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
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

    public List<Venta> findByClienteId(Long clienteId) {
        return repository.findByClienteId(clienteId);
    }

    public List<Venta> findByFechaBetween(LocalDateTime from, LocalDateTime to) {
        return repository.findByFechaBetween(from, to);
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
