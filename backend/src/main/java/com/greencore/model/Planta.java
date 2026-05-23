/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que representa una planta cultivada en el invernadero, trazable por lote.
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

@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
@Entity
@Table(name = "plantas")
public class Planta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "nombre", nullable = false, length = 150)
    private String nombre;

    @Column(name = "especie", nullable = false, length = 200)
    private String especie;

    @Column(name = "lote", nullable = false, unique = true, length = 50)
    private String lote;

    @Column(name = "cantidad", nullable = false)
    private Integer cantidad;

    @Column(name = "precio", nullable = false, precision = 10, scale = 2)
    private BigDecimal precio;

    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false, length = 30)
    private EstadoPlanta estado = EstadoPlanta.SEMILLA;

    @Column(name = "fechaSiembra", nullable = false)
    private LocalDate fechaSiembra;

    @Column(name = "fechaEstimadaVenta")
    private LocalDate fechaEstimadaVenta;

    @Column(name = "descripcion", columnDefinition = "TEXT")
    private String descripcion;

    @Column(name = "imagenUrl", columnDefinition = "TEXT")
    private String imagenUrl;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zona_id", nullable = false)
    private Zona zona;

    @Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;

    public Planta() {}

    @PrePersist
    void prePersist() {
        if (creadoEn == null) creadoEn = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }

    public String getEspecie() { return especie; }
    public void setEspecie(String especie) { this.especie = especie; }

    public String getLote() { return lote; }
    public void setLote(String lote) { this.lote = lote; }

    public Integer getCantidad() { return cantidad; }
    public void setCantidad(Integer cantidad) { this.cantidad = cantidad; }

    public BigDecimal getPrecio() { return precio; }
    public void setPrecio(BigDecimal precio) { this.precio = precio; }

    public EstadoPlanta getEstado() { return estado; }
    public void setEstado(EstadoPlanta estado) { this.estado = estado; }

    public LocalDate getFechaSiembra() { return fechaSiembra; }
    public void setFechaSiembra(LocalDate fechaSiembra) { this.fechaSiembra = fechaSiembra; }

    public LocalDate getFechaEstimadaVenta() { return fechaEstimadaVenta; }
    public void setFechaEstimadaVenta(LocalDate fechaEstimadaVenta) { this.fechaEstimadaVenta = fechaEstimadaVenta; }

    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }

    public String getImagenUrl() { return imagenUrl; }
    public void setImagenUrl(String imagenUrl) { this.imagenUrl = imagenUrl; }

    public Zona getZona() { return zona; }
    public void setZona(Zona zona) { this.zona = zona; }

    public LocalDateTime getCreadoEn() { return creadoEn; }
    public void setCreadoEn(LocalDateTime creadoEn) { this.creadoEn = creadoEn; }
}
