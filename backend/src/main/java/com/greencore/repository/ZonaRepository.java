/**
 * GreenCore — Sistema de gestion de invernadero
 * Repositorio JPA para acceso a datos de la entidad Zona.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.repository;

import com.greencore.model.Zona;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ZonaRepository extends JpaRepository<Zona, Long> {
}