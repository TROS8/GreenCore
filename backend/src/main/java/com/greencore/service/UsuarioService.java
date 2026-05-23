package com.greencore.service;

import com.greencore.model.Role;
import com.greencore.model.Usuario;
import com.greencore.repository.UsuarioRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class UsuarioService {

    private final UsuarioRepository repository;

    public UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    public List<Usuario> findAll() {
        return repository.findAll();
    }

    public Optional<Usuario> findById(Long id) {
        return repository.findById(id);
    }

    public Usuario save(Usuario entity) {
        return repository.save(entity);
    }

    public void delete(Long id) {
        repository.deleteById(id);
    }

    public Optional<Usuario> findByProviderId(String providerId) {
        return repository.findByProviderId(providerId);
    }

    public Usuario upsertGoogleUser(String email, String nombre, String fotoPerfil, String providerId) {
        return repository.findByProviderId(providerId)
                .map(usuario -> {
                    usuario.setEmail(email);
                    usuario.setNombre(nombre);
                    usuario.setFotoPerfil(fotoPerfil);
                    usuario.setActivo(true);
                    usuario.setUltimoAcceso(LocalDateTime.now());
                    return repository.save(usuario);
                })
                .orElseGet(() -> {
                    Usuario usuario = new Usuario();
                    usuario.setEmail(email);
                    usuario.setNombre(nombre);
                    usuario.setFotoPerfil(fotoPerfil);
                    usuario.setProvider("GOOGLE");
                    usuario.setProviderId(providerId);
                    usuario.setRol(Role.OPERARIO);
                    usuario.setActivo(true);
                    usuario.setCreadoEn(LocalDateTime.now());
                    usuario.setUltimoAcceso(LocalDateTime.now());
                    return repository.save(usuario);
                });
    }
}
