package com.greencore;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class AlertaControllerTest {

    private static final ParameterizedTypeReference<Map<String, Object>> MAP_TYPE =
            new ParameterizedTypeReference<>() {};
    private static final ParameterizedTypeReference<List<Map<String, Object>>> LIST_TYPE =
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

    /** Creates Zona + Sensor, then posts an out-of-range reading to generate an Alerta. */
    private Long createAlertaViaLectura() {
        Map<String, Object> zonaPayload = Map.of(
                "nombre", "ZonaAlerta-" + UUID.randomUUID().toString().substring(0, 8),
                "capacidadMaxima", 20,
                "temperaturaMinima", 10.0,
                "temperaturaMaxima", 30.0,
                "humedadMinima", 40.0,
                "humedadMaxima", 80.0,
                "activa", true
        );
        Long zonaId = ((Number) restTemplate.exchange(
                url("/api/v1/zonas"), HttpMethod.POST,
                new HttpEntity<>(zonaPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();

        Map<String, Object> sensorPayload = Map.of(
                "codigo", "SEN-ALT-" + UUID.randomUUID().toString().substring(0, 8),
                "tipo", "TEMPERATURA",
                "unidad", "°C",
                "umbralMinimo", 15.0,
                "umbralMaximo", 25.0,
                "estado", "ACTIVO",
                "zona", Map.of("id", zonaId)
        );
        Long sensorId = ((Number) restTemplate.exchange(
                url("/api/v1/sensores"), HttpMethod.POST,
                new HttpEntity<>(sensorPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();

        // Post a value (50.0) that is clearly above umbralMaximo (25.0) → triggers alerta
        restTemplate.exchange(
                url("/api/v1/sensores/" + sensorId + "/lectura"), HttpMethod.POST,
                new HttpEntity<>(Map.of("valor", 50.0), authHeaders()), MAP_TYPE);

        // Return the first alerta ID from the list
        List<Map<String, Object>> alertas = restTemplate.exchange(
                url("/api/v1/alertas"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), LIST_TYPE).getBody();
        return ((Number) alertas.get(0).get("id")).longValue();
    }

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/alertas"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/alertas"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void outOfRangeLectura_generatesAlerta() {
        createAlertaViaLectura();
        List<Map<String, Object>> alertas = restTemplate.exchange(
                url("/api/v1/alertas"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), LIST_TYPE).getBody();
        assertThat(alertas).isNotEmpty();
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/alertas/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
