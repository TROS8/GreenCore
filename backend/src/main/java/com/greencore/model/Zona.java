/**
 * GreenCore — Sistema de gestión de invernadero
 * Entidad JPA que representa una zona física del invernadero.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Zona física del invernadero con condiciones ambientales controladas.
 * Tabla BD: {@code zonas}. Entidad raíz: plantas y sensores siempre pertenecen a una zona.
 */
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
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

    @PrePersist
    void prePersist() {
        if (creadoEn == null) creadoEn = LocalDateTime.now();
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

    public Integer getCapacidadMaxima() {
        return this.capacidadMaxima;
    }

    public void setCapacidadMaxima(Integer capacidadMaxima) {
        this.capacidadMaxima = capacidadMaxima;
    }

    public Double getTemperaturaMinima() {
        return this.temperaturaMinima;
    }

    public void setTemperaturaMinima(Double temperaturaMinima) {
        this.temperaturaMinima = temperaturaMinima;
    }

    public Double getTemperaturaMaxima() {
        return this.temperaturaMaxima;
    }

    public void setTemperaturaMaxima(Double temperaturaMaxima) {
        this.temperaturaMaxima = temperaturaMaxima;
    }

    public Double getHumedadMinima() {
        return this.humedadMinima;
    }

    public void setHumedadMinima(Double humedadMinima) {
        this.humedadMinima = humedadMinima;
    }

    public Double getHumedadMaxima() {
        return this.humedadMaxima;
    }

    public void setHumedadMaxima(Double humedadMaxima) {
        this.humedadMaxima = humedadMaxima;
    }

    public Boolean getActiva() {
        return this.activa;
    }

    public void setActiva(Boolean activa) {
        this.activa = activa;
    }

    public LocalDateTime getCreadoEn() {
        return this.creadoEn;
    }

    public void setCreadoEn(LocalDateTime creadoEn) {
        this.creadoEn = creadoEn;
    }

}