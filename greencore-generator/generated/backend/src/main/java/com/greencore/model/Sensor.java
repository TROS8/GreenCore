package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "sensores")
public class Sensor {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "codigo", nullable = false, unique = true)
    private String codigo;

    @Enumerated(EnumType.STRING)
@Column(name = "tipo", nullable = false)
    private Enum tipo;

@Column(name = "valorActual")
    private Double valorActual;

@Column(name = "unidad", nullable = false)
    private String unidad;

@Column(name = "umbralMinimo", nullable = false)
    private Double umbralMinimo;

@Column(name = "umbralMaximo", nullable = false)
    private Double umbralMaximo;

    @Enumerated(EnumType.STRING)
@Column(name = "estado", nullable = false, columnDefinition = "VARCHAR(20) DEFAULT 'ACTIVO'")
    private Enum estado;

@Column(name = "ultimaLectura")
    private LocalDateTime ultimaLectura;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zona_id")
@Column(name = "zona", nullable = false)
    private Zona zona;

@Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;


    public Sensor() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getCodigo() {
        return this.codigo;
    }

    public void setCodigo(String codigo) {
        this.codigo = codigo;
    }

    public Enum getTipo() {
        return this.tipo;
    }

    public void setTipo(Enum tipo) {
        this.tipo = tipo;
    }

    public Double getValoractual() {
        return this.valorActual;
    }

    public void setValoractual(Double valorActual) {
        this.valorActual = valorActual;
    }

    public String getUnidad() {
        return this.unidad;
    }

    public void setUnidad(String unidad) {
        this.unidad = unidad;
    }

    public Double getUmbralminimo() {
        return this.umbralMinimo;
    }

    public void setUmbralminimo(Double umbralMinimo) {
        this.umbralMinimo = umbralMinimo;
    }

    public Double getUmbralmaximo() {
        return this.umbralMaximo;
    }

    public void setUmbralmaximo(Double umbralMaximo) {
        this.umbralMaximo = umbralMaximo;
    }

    public Enum getEstado() {
        return this.estado;
    }

    public void setEstado(Enum estado) {
        this.estado = estado;
    }

    public LocalDateTime getUltimalectura() {
        return this.ultimaLectura;
    }

    public void setUltimalectura(LocalDateTime ultimaLectura) {
        this.ultimaLectura = ultimaLectura;
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