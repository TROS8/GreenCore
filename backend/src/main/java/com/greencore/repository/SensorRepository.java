/**
 * GreenCore — Sistema de gestion de invernadero
 * Repositorio JPA para acceso a datos de la entidad Sensor.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.repository;

import com.greencore.model.Sensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SensorRepository extends JpaRepository<Sensor, Long> {
}