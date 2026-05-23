/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que representa una venta de plantas a un cliente.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
@Entity
@Table(name = "ventas")
public class Venta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "numeroFactura", nullable = false, unique = true, length = 30)
    private String numeroFactura;

    @Column(name = "cantidad", nullable = false)
    private Integer cantidad;

    @Column(name = "precioUnitario", nullable = false, precision = 10, scale = 2)
    private BigDecimal precioUnitario;

    @Column(name = "total", nullable = false, precision = 12, scale = 2)
    private BigDecimal total;

    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false, length = 20)
    private EstadoVenta estado = EstadoVenta.PENDIENTE;

    @Column(name = "notas", columnDefinition = "TEXT")
    private String notas;

    @Column(name = "fecha", nullable = false)
    private LocalDateTime fecha;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "planta_id", nullable = false)
    private Planta planta;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "usuario_id")
    private Usuario registradoPor;

    public Venta() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNumeroFactura() { return numeroFactura; }
    public void setNumeroFactura(String numeroFactura) { this.numeroFactura = numeroFactura; }

    public Integer getCantidad() { return cantidad; }
    public void setCantidad(Integer cantidad) { this.cantidad = cantidad; }

    public BigDecimal getPrecioUnitario() { return precioUnitario; }
    public void setPrecioUnitario(BigDecimal precioUnitario) { this.precioUnitario = precioUnitario; }

    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal total) { this.total = total; }

    public EstadoVenta getEstado() { return estado; }
    public void setEstado(EstadoVenta estado) { this.estado = estado; }

    public String getNotas() { return notas; }
    public void setNotas(String notas) { this.notas = notas; }

    public LocalDateTime getFecha() { return fecha; }
    public void setFecha(LocalDateTime fecha) { this.fecha = fecha; }

    public Planta getPlanta() { return planta; }
    public void setPlanta(Planta planta) { this.planta = planta; }

    public Cliente getCliente() { return cliente; }
    public void setCliente(Cliente cliente) { this.cliente = cliente; }

    public Usuario getRegistradoPor() { return registradoPor; }
    public void setRegistradoPor(Usuario registradoPor) { this.registradoPor = registradoPor; }
}
