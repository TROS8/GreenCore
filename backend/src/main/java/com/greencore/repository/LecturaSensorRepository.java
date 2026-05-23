package com.greencore.repository;

import com.greencore.model.LecturaSensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LecturaSensorRepository extends JpaRepository<LecturaSensor, Long> {
    List<LecturaSensor> findBySensorIdOrderByTimestampDesc(Long sensorId);
}
