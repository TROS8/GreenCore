/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para la entidad Cliente.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.Cliente;
import com.greencore.repository.ClienteRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ClienteService {

    private final ClienteRepository repository;

    public ClienteService(ClienteRepository repository) {
        this.repository = repository;
    }

    public List<Cliente> findAll() {
        return repository.findAll();
    }

    public Optional<Cliente> findById(Long id) {
        return repository.findById(id);
    }

    public Cliente save(Cliente entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }
}