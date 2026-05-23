package com.greencore.repository;

import com.greencore.model.Planta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PlantaRepository extends JpaRepository<Planta, Long> {
    List<Planta> findByZonaId(Long zonaId);
}
