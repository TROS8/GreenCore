/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que representa un usuario autenticado via Google OAuth2.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "usuarios")
public class Usuario {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "email", nullable = false, unique = true, length = 255)
    private String email;

    @Column(name = "nombre", nullable = false, length = 150)
    private String nombre;

    @Column(name = "fotoPerfil", columnDefinition = "TEXT")
    private String fotoPerfil;

    @Enumerated(EnumType.STRING)
    @Column(name = "rol", nullable = false, length = 30)
    private Role rol = Role.OPERARIO;

    @Column(name = "provider", nullable = false, length = 30)
    private String provider = "GOOGLE";

    @Column(name = "providerId", nullable = false, unique = true, length = 255)
    private String providerId;

    @Column(name = "activo", nullable = false)
    private Boolean activo = true;

    @Column(name = "ultimoAcceso")
    private LocalDateTime ultimoAcceso;

    @Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;

    public Usuario() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }

    public String getFotoPerfil() { return fotoPerfil; }
    public void setFotoPerfil(String fotoPerfil) { this.fotoPerfil = fotoPerfil; }

    public Role getRol() { return rol; }
    public void setRol(Role rol) { this.rol = rol; }

    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }

    public String getProviderId() { return providerId; }
    public void setProviderId(String providerId) { this.providerId = providerId; }

    public Boolean getActivo() { return activo; }
    public void setActivo(Boolean activo) { this.activo = activo; }

    public LocalDateTime getUltimoAcceso() { return ultimoAcceso; }
    public void setUltimoAcceso(LocalDateTime ultimoAcceso) { this.ultimoAcceso = ultimoAcceso; }

    public LocalDateTime getCreadoEn() { return creadoEn; }
    public void setCreadoEn(LocalDateTime creadoEn) { this.creadoEn = creadoEn; }
}
