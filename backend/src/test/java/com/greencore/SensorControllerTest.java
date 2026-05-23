package com.greencore;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;

import java.util.Map;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class SensorControllerTest {

    private static final ParameterizedTypeReference<Map<String, Object>> MAP_TYPE =
            new ParameterizedTypeReference<>() {};

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    private String url(String path) {
        return "http://localhost:" + port + path;
    }

    private HttpHeaders authHeaders() {
        HttpHeaders h = new HttpHeaders();
        h.setBearerAuth(TestTokenHelper.generate());
        h.setContentType(MediaType.APPLICATION_JSON);
        return h;
    }

    /** Creates a Zona and returns its ID (prerequisite for Sensor). */
    private Long createZona() {
        Map<String, Object> payload = Map.of(
                "nombre", "ZonaSensor-" + UUID.randomUUID().toString().substring(0, 8),
                "capacidadMaxima", 30,
                "temperaturaMinima", 10.0,
                "temperaturaMaxima", 35.0,
                "humedadMinima", 30.0,
                "humedadMaxima", 90.0,
                "activa", true
        );
        ResponseEntity<Map<String, Object>> r = restTemplate.exchange(
                url("/api/v1/zonas"), HttpMethod.POST,
                new HttpEntity<>(payload, authHeaders()), MAP_TYPE);
        return ((Number) r.getBody().get("id")).longValue();
    }

    private Map<String, Object> sensorPayload(Long zonaId) {
        return Map.of(
                "codigo", "SEN-" + UUID.randomUUID().toString().substring(0, 8),
                "tipo", "TEMPERATURA",
                "unidad", "°C",
                "umbralMinimo", 10.0,
                "umbralMaximo", 40.0,
                "estado", "ACTIVO",
                "zona", Map.of("id", zonaId)
        );
    }

    private ResponseEntity<Map<String, Object>> postSensor(Long zonaId) {
        return restTemplate.exchange(
                url("/api/v1/sensores"), HttpMethod.POST,
                new HttpEntity<>(sensorPayload(zonaId), authHeaders()), MAP_TYPE);
    }

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/sensores"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/sensores"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void create_returnsCreated() {
        ResponseEntity<Map<String, Object>> r = postSensor(createZona());
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody()).containsKey("id");
    }

    @Test
    void getById_returnsSensor() {
        Long id = ((Number) postSensor(createZona()).getBody().get("id")).longValue();
        ResponseEntity<String> found = restTemplate.exchange(
                url("/api/v1/sensores/" + id), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(found.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/sensores/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void delete_returnsNoContent() {
        Long id = ((Number) postSensor(createZona()).getBody().get("id")).longValue();
        ResponseEntity<Void> deleted = restTemplate.exchange(
                url("/api/v1/sensores/" + id), HttpMethod.DELETE,
                new HttpEntity<>(authHeaders()), Void.class);
        assertThat(deleted.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);
    }

    @Test
    void registrarLectura_returnsCreated() {
        Long sensorId = ((Number) postSensor(createZona()).getBody().get("id")).longValue();
        ResponseEntity<Map<String, Object>> r = restTemplate.exchange(
                url("/api/v1/sensores/" + sensorId + "/lectura"), HttpMethod.POST,
                new HttpEntity<>(Map.of("valor", 25.5), authHeaders()), MAP_TYPE);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody()).containsKey("id");
    }
}
