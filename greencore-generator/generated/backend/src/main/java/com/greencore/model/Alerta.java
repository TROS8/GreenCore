package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "alertas")
public class Alerta {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "mensaje", nullable = false)
    private String mensaje;

    @Enumerated(EnumType.STRING)
@Column(name = "nivel", nullable = false, columnDefinition = "VARCHAR(20) DEFAULT 'ADVERTENCIA'")
    private Enum nivel;

@Column(name = "leida", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'False'")
    private Boolean leida;

@Column(name = "correoEnviado", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'False'")
    private Boolean correoEnviado;

@Column(name = "valorRegistrado", nullable = false)
    private Double valorRegistrado;

@Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sensor_id")
@Column(name = "sensor", nullable = false)
    private Sensor sensor;


    public Alerta() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getMensaje() {
        return this.mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public Enum getNivel() {
        return this.nivel;
    }

    public void setNivel(Enum nivel) {
        this.nivel = nivel;
    }

    public Boolean getLeida() {
        return this.leida;
    }

    public void setLeida(Boolean leida) {
        this.leida = leida;
    }

    public Boolean getCorreoenviado() {
        return this.correoEnviado;
    }

    public void setCorreoenviado(Boolean correoEnviado) {
        this.correoEnviado = correoEnviado;
    }

    public Double getValorregistrado() {
        return this.valorRegistrado;
    }

    public void setValorregistrado(Double valorRegistrado) {
        this.valorRegistrado = valorRegistrado;
    }

    public LocalDateTime getTimestamp() {
        return this.timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public Sensor getSensor() {
        return this.sensor;
    }

    public void setSensor(Sensor sensor) {
        this.sensor = sensor;
    }

}