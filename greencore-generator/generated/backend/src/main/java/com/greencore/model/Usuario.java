package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "usuarios")
public class Usuario {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "email", nullable = false, unique = true)
    private String email;

@Column(name = "nombre", nullable = false)
    private String nombre;

@Column(name = "fotoPerfil")
    private String fotoPerfil;

    @Enumerated(EnumType.STRING)
@Column(name = "rol", nullable = false, columnDefinition = "VARCHAR(30) DEFAULT 'OPERARIO'")
    private Enum rol;

@Column(name = "provider", nullable = false, columnDefinition = "VARCHAR(30) DEFAULT 'GOOGLE'")
    private String provider;

@Column(name = "providerId", nullable = false, unique = true)
    private String providerId;

@Column(name = "activo", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'True'")
    private Boolean activo;

@Column(name = "ultimoAcceso")
    private LocalDateTime ultimoAcceso;

@Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;


    public Usuario() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getNombre() {
        return this.nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getFotoperfil() {
        return this.fotoPerfil;
    }

    public void setFotoperfil(String fotoPerfil) {
        this.fotoPerfil = fotoPerfil;
    }

    public Enum getRol() {
        return this.rol;
    }

    public void setRol(Enum rol) {
        this.rol = rol;
    }

    public String getProvider() {
        return this.provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public String getProviderid() {
        return this.providerId;
    }

    public void setProviderid(String providerId) {
        this.providerId = providerId;
    }

    public Boolean getActivo() {
        return this.activo;
    }

    public void setActivo(Boolean activo) {
        this.activo = activo;
    }

    public LocalDateTime getUltimoacceso() {
        return this.ultimoAcceso;
    }

    public void setUltimoacceso(LocalDateTime ultimoAcceso) {
        this.ultimoAcceso = ultimoAcceso;
    }

    public LocalDateTime getCreadoen() {
        return this.creadoEn;
    }

    public void setCreadoen(LocalDateTime creadoEn) {
        this.creadoEn = creadoEn;
    }

}