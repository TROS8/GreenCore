package com.greencore.repository;

import com.greencore.model.LecturaSensor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface LecturaSensorRepository extends JpaRepository<LecturaSensor, Long> {
}