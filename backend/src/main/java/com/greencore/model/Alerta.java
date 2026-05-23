/**
 * GreenCore — Sistema de gestion de invernadero
 * Entidad JPA que representa una alerta generada automaticamente por un sensor fuera de rango.
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
@Table(name = "alertas")
public class Alerta {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "mensaje", nullable = false)
    private String mensaje;

    @Enumerated(EnumType.STRING)
    @Column(name = "nivel", nullable = false, length = 20)
    private NivelAlerta nivel;

    @Column(name = "leida", nullable = false)
    private Boolean leida = false;

    @Column(name = "correoEnviado", nullable = false)
    private Boolean correoEnviado = false;

    @Column(name = "valorRegistrado", nullable = false)
    private Double valorRegistrado;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sensor_id", nullable = false)
    private Sensor sensor;

    public Alerta() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }

    public NivelAlerta getNivel() { return nivel; }
    public void setNivel(NivelAlerta nivel) { this.nivel = nivel; }

    public Boolean getLeida() { return leida; }
    public void setLeida(Boolean leida) { this.leida = leida; }

    public Boolean getCorreoEnviado() { return correoEnviado; }
    public void setCorreoEnviado(Boolean correoEnviado) { this.correoEnviado = correoEnviado; }

    public Double getValorRegistrado() { return valorRegistrado; }
    public void setValorRegistrado(Double valorRegistrado) { this.valorRegistrado = valorRegistrado; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }

    public Sensor getSensor() { return sensor; }
    public void setSensor(Sensor sensor) { this.sensor = sensor; }
}
