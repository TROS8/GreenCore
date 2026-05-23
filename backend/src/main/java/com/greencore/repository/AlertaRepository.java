/**
 * GreenCore — Sistema de gestion de invernadero
 * Repositorio JPA para acceso a datos de la entidad Alerta.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.repository;

import com.greencore.model.Alerta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AlertaRepository extends JpaRepository<Alerta, Long> {
    List<Alerta> findByLeidaFalse();
}
