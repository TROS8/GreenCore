package com.greencore.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "lecturas_sensor")
public class LecturaSensor {

@Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
@Column(name = "id")
    private Long id;

@Column(name = "valor", nullable = false)
    private Double valor;

@Column(name = "fueraDeRango", nullable = false, columnDefinition = "BOOLEAN DEFAULT 'False'")
    private Boolean fueraDeRango;

@Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sensor_id")
@Column(name = "sensor", nullable = false)
    private Sensor sensor;


    public LecturaSensor() {
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Double getValor() {
        return this.valor;
    }

    public void setValor(Double valor) {
        this.valor = valor;
    }

    public Boolean getFueraderango() {
        return this.fueraDeRango;
    }

    public void setFueraderango(Boolean fueraDeRango) {
        this.fueraDeRango = fueraDeRango;
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