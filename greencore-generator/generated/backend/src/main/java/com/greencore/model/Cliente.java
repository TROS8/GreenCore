package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "clientes")
public class Cliente {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "nombre", nullable = false)
    private String nombre;

@Column(name = "email", nullable = false, unique = true)
    private String email;

@Column(name = "telefono")
    private String telefono;

@Column(name = "ciudad")
    private String ciudad;

@Column(name = "activo", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'True'")
    private Boolean activo;

@Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;


    public Cliente() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombre() {
        return this.nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getTelefono() {
        return this.telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public String getCiudad() {
        return this.ciudad;
    }

    public void setCiudad(String ciudad) {
        this.ciudad = ciudad;
    }

    public Boolean getActivo() {
        return this.activo;
    }

    public void setActivo(Boolean activo) {
        this.activo = activo;
    }

    public LocalDateTime getCreadoen() {
        return this.creadoEn;
    }

    public void setCreadoen(LocalDateTime creadoEn) {
        this.creadoEn = creadoEn;
    }

}