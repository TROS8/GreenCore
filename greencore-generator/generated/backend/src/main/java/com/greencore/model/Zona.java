package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "zonas")
public class Zona {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "nombre", nullable = false, unique = true)
    private String nombre;

@Column(name = "descripcion")
    private String descripcion;

@Column(name = "capacidadMaxima", nullable = false)
    private Integer capacidadMaxima;

@Column(name = "temperaturaMinima", nullable = false)
    private Double temperaturaMinima;

@Column(name = "temperaturaMaxima", nullable = false)
    private Double temperaturaMaxima;

@Column(name = "humedadMinima", nullable = false)
    private Double humedadMinima;

@Column(name = "humedadMaxima", nullable = false)
    private Double humedadMaxima;

@Column(name = "activa", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'True'")
    private Boolean activa;

@Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;


    public Zona() {
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

    public String getDescripcion() {
        return this.descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public Integer getCapacidadmaxima() {
        return this.capacidadMaxima;
    }

    public void setCapacidadmaxima(Integer capacidadMaxima) {
        this.capacidadMaxima = capacidadMaxima;
    }

    public Double getTemperaturaminima() {
        return this.temperaturaMinima;
    }

    public void setTemperaturaminima(Double temperaturaMinima) {
        this.temperaturaMinima = temperaturaMinima;
    }

    public Double getTemperaturamaxima() {
        return this.temperaturaMaxima;
    }

    public void setTemperaturamaxima(Double temperaturaMaxima) {
        this.temperaturaMaxima = temperaturaMaxima;
    }

    public Double getHumedadminima() {
        return this.humedadMinima;
    }

    public void setHumedadminima(Double humedadMinima) {
        this.humedadMinima = humedadMinima;
    }

    public Double getHumedadmaxima() {
        return this.humedadMaxima;
    }

    public void setHumedadmaxima(Double humedadMaxima) {
        this.humedadMaxima = humedadMaxima;
    }

    public Boolean getActiva() {
        return this.activa;
    }

    public void setActiva(Boolean activa) {
        this.activa = activa;
    }

    public LocalDateTime getCreadoen() {
        return this.creadoEn;
    }

    public void setCreadoen(LocalDateTime creadoEn) {
        this.creadoEn = creadoEn;
    }

}