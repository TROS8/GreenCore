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
class LecturaSensorControllerTest {

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

    private Long createSensorWithZona() {
        Map<String, Object> zonaPayload = Map.of(
                "nombre", "ZonaLec-" + UUID.randomUUID().toString().substring(0, 8),
                "capacidadMaxima", 10,
                "temperaturaMinima", 5.0,
                "temperaturaMaxima", 40.0,
                "humedadMinima", 20.0,
                "humedadMaxima", 90.0,
                "activa", true
        );
        Long zonaId = ((Number) restTemplate.exchange(
                url("/api/v1/zonas"), HttpMethod.POST,
                new HttpEntity<>(zonaPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();

        Map<String, Object> sensorPayload = Map.of(
                "codigo", "SEN-LEC-" + UUID.randomUUID().toString().substring(0, 8),
                "tipo", "HUMEDAD",
                "unidad", "%",
                "umbralMinimo", 30.0,
                "umbralMaximo", 80.0,
                "estado", "ACTIVO",
                "zona", Map.of("id", zonaId)
        );
        return ((Number) restTemplate.exchange(
                url("/api/v1/sensores"), HttpMethod.POST,
                new HttpEntity<>(sensorPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();
    }

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/lecturas_sensor"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/lecturas_sensor"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void registrarLectura_createsRecord() {
        Long sensorId = createSensorWithZona();
        ResponseEntity<Map<String, Object>> r = restTemplate.exchange(
                url("/api/v1/sensores/" + sensorId + "/lectura"), HttpMethod.POST,
                new HttpEntity<>(Map.of("valor", 55.0), authHeaders()), MAP_TYPE);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody().get("valor")).isEqualTo(55.0);
        assertThat(r.getBody().get("fueraDeRango")).isEqualTo(false);
    }

    @Test
    void registrarLectura_outOfRange_setsFlag() {
        Long sensorId = createSensorWithZona();
        ResponseEntity<Map<String, Object>> r = restTemplate.exchange(
                url("/api/v1/sensores/" + sensorId + "/lectura"), HttpMethod.POST,
                new HttpEntity<>(Map.of("valor", 95.0), authHeaders()), MAP_TYPE);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody().get("fueraDeRango")).isEqualTo(true);
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/lecturas_sensor/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
