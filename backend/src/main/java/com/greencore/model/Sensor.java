/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que representa un sensor fisico instalado en una zona del invernadero.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
@Entity
@Table(name = "sensores")
public class Sensor {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "codigo", nullable = false, unique = true, length = 50)
    private String codigo;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo", nullable = false, length = 30)
    private TipoSensor tipo;

    @Column(name = "valorActual")
    private Double valorActual;

    @Column(name = "unidad", nullable = false, length = 20)
    private String unidad;

    @Column(name = "umbralMinimo", nullable = false)
    private Double umbralMinimo;

    @Column(name = "umbralMaximo", nullable = false)
    private Double umbralMaximo;

    @Enumerated(EnumType.STRING)
    @Column(name = "estado", nullable = false, length = 20)
    private EstadoSensor estado = EstadoSensor.ACTIVO;

    @Column(name = "ultimaLectura")
    private LocalDateTime ultimaLectura;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "zona_id", nullable = false)
    private Zona zona;

    @Column(name = "creadoEn", nullable = false)
    private LocalDateTime creadoEn;

    public Sensor() {}

    @PrePersist
    void prePersist() {
        if (creadoEn == null) creadoEn = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCodigo() { return codigo; }
    public void setCodigo(String codigo) { this.codigo = codigo; }

    public TipoSensor getTipo() { return tipo; }
    public void setTipo(TipoSensor tipo) { this.tipo = tipo; }

    public Double getValorActual() { return valorActual; }
    public void setValorActual(Double valorActual) { this.valorActual = valorActual; }

    public String getUnidad() { return unidad; }
    public void setUnidad(String unidad) { this.unidad = unidad; }

    public Double getUmbralMinimo() { return umbralMinimo; }
    public void setUmbralMinimo(Double umbralMinimo) { this.umbralMinimo = umbralMinimo; }

    public Double getUmbralMaximo() { return umbralMaximo; }
    public void setUmbralMaximo(Double umbralMaximo) { this.umbralMaximo = umbralMaximo; }

    public EstadoSensor getEstado() { return estado; }
    public void setEstado(EstadoSensor estado) { this.estado = estado; }

    public LocalDateTime getUltimaLectura() { return ultimaLectura; }
    public void setUltimaLectura(LocalDateTime ultimaLectura) { this.ultimaLectura = ultimaLectura; }

    public Zona getZona() { return zona; }
    public void setZona(Zona zona) { this.zona = zona; }

    public LocalDateTime getCreadoEn() { return creadoEn; }
    public void setCreadoEn(LocalDateTime creadoEn) { this.creadoEn = creadoEn; }
}
