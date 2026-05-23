package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "ventas")
public class Venta {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "numeroFactura", nullable = false, unique = true)
    private String numeroFactura;

@Column(name = "cantidad", nullable = false)
    private Integer cantidad;

@Column(name = "precioUnitario", nullable = false)
    private BigDecimal precioUnitario;

@Column(name = "total", nullable = false)
    private BigDecimal total;

    @Enumerated(EnumType.STRING)
@Column(name = "estado", nullable = false, columnDefinition = "VARCHAR(20) DEFAULT 'PENDIENTE'")
    private Enum estado;

@Column(name = "notas")
    private String notas;

@Column(name = "fecha", nullable = false)
    private LocalDateTime fecha;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "planta_id")
@Column(name = "planta", nullable = false)
    private Planta planta;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cliente_id")
@Column(name = "cliente", nullable = false)
    private Cliente cliente;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "usuario_id")
@Column(name = "registradoPor", nullable = false)
    private Usuario registradoPor;


    public Venta() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNumerofactura() {
        return this.numeroFactura;
    }

    public void setNumerofactura(String numeroFactura) {
        this.numeroFactura = numeroFactura;
    }

    public Integer getCantidad() {
        return this.cantidad;
    }

    public void setCantidad(Integer cantidad) {
        this.cantidad = cantidad;
    }

    public BigDecimal getPreciounitario() {
        return this.precioUnitario;
    }

    public void setPreciounitario(BigDecimal precioUnitario) {
        this.precioUnitario = precioUnitario;
    }

    public BigDecimal getTotal() {
        return this.total;
    }

    public void setTotal(BigDecimal total) {
        this.total = total;
    }

    public Enum getEstado() {
        return this.estado;
    }

    public void setEstado(Enum estado) {
        this.estado = estado;
    }

    public String getNotas() {
        return this.notas;
    }

    public void setNotas(String notas) {
        this.notas = notas;
    }

    public LocalDateTime getFecha() {
        return this.fecha;
    }

    public void setFecha(LocalDateTime fecha) {
        this.fecha = fecha;
    }

    public Planta getPlanta() {
        return this.planta;
    }

    public void setPlanta(Planta planta) {
        this.planta = planta;
    }

    public Cliente getCliente() {
        return this.cliente;
    }

    public void setCliente(Cliente cliente) {
        this.cliente = cliente;
    }

    public Usuario getRegistradopor() {
        return this.registradoPor;
    }

    public void setRegistradopor(Usuario registradoPor) {
        this.registradoPor = registradoPor;
    }

}