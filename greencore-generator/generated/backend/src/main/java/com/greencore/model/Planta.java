package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "plantas")
public class Planta {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "nombre", nullable = false)
    private String nombre;

@Column(name = "especie", nullable = false)
    private String especie;

@Column(name = "lote", nullable = false, unique = true)
    private String lote;

@Column(name = "cantidad", nullable = false)
    private Integer cantidad;

@Column(name = "precio", nullable = false)
    private BigDecimal precio;

    @Enumerated(EnumType.STRING)
@Column(name = "estado", nullable = false, columnDefinition = "VARCHAR(30) DEFAULT 'SEMILLA'")
    private Enum estado;

@Column(name = "fechaSiembra", nullable = false)
    private LocalDate fechaSiembra;

@Column(name = "fechaEstimadaVenta")
    private LocalDate fechaEstimadaVenta;

@Column(name = "descripcion")
    private String descripcion;

@Column(name = "imagenUrl")
    private String imagenUrl;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zona_id")
@Column(name = "zona", nullable = false)
    private Zona zona;

@Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;


    public Planta() {
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

    public String getEspecie() {
        return this.especie;
    }

    public void setEspecie(String especie) {
        this.especie = especie;
    }

    public String getLote() {
        return this.lote;
    }

    public void setLote(String lote) {
        this.lote = lote;
    }

    public Integer getCantidad() {
        return this.cantidad;
    }

    public void setCantidad(Integer cantidad) {
        this.cantidad = cantidad;
    }

    public BigDecimal getPrecio() {
        return this.precio;
    }

    public void setPrecio(BigDecimal precio) {
        this.precio = precio;
    }

    public Enum getEstado() {
        return this.estado;
    }

    public void setEstado(Enum estado) {
        this.estado = estado;
    }

    public LocalDate getFechasiembra() {
        return this.fechaSiembra;
    }

    public void setFechasiembra(LocalDate fechaSiembra) {
        this.fechaSiembra = fechaSiembra;
    }

    public LocalDate getFechaestimadaventa() {
        return this.fechaEstimadaVenta;
    }

    public void setFechaestimadaventa(LocalDate fechaEstimadaVenta) {
        this.fechaEstimadaVenta = fechaEstimadaVenta;
    }

    public String getDescripcion() {
        return this.descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getImagenurl() {
        return this.imagenUrl;
    }

    public void setImagenurl(String imagenUrl) {
        this.imagenUrl = imagenUrl;
    }

    public Zona getZona() {
        return this.zona;
    }

    public void setZona(Zona zona) {
        this.zona = zona;
    }

    public LocalDateTime getCreadoen() {
        return this.creadoEn;
    }

    public void setCreadoen(LocalDateTime creadoEn) {
        this.creadoEn = creadoEn;
    }

}