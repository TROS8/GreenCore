/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que registra una lectura historica de un sensor.
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
    @JoinColumn(name = "sensor_id", nullable = false)
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

    public Boolean getFueraDeRango() {
        return this.fueraDeRango;
    }

    public void setFueraDeRango(Boolean fueraDeRango) {
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