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
class VentaControllerTest {

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

    private Long createPlantaWithZona() {
        Map<String, Object> zonaPayload = Map.of(
                "nombre", "ZonaVenta-" + UUID.randomUUID().toString().substring(0, 8),
                "capacidadMaxima", 50,
                "temperaturaMinima", 12.0,
                "temperaturaMaxima", 28.0,
                "humedadMinima", 40.0,
                "humedadMaxima", 75.0,
                "activa", true
        );
        Long zonaId = ((Number) restTemplate.exchange(
                url("/api/v1/zonas"), HttpMethod.POST,
                new HttpEntity<>(zonaPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();

        Map<String, Object> plantaPayload = Map.of(
                "nombre", "Albahaca",
                "especie", "Ocimum basilicum",
                "lote", "LOT-" + UUID.randomUUID().toString().substring(0, 8),
                "cantidad", 50,
                "precio", 1.80,
                "estado", "LISTO_VENTA",
                "fechaSiembra", "2026-01-01",
                "zona", Map.of("id", zonaId)
        );
        return ((Number) restTemplate.exchange(
                url("/api/v1/plantas"), HttpMethod.POST,
                new HttpEntity<>(plantaPayload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();
    }

    private Long createCliente() {
        Map<String, Object> payload = Map.of(
                "nombre", "Cliente Venta",
                "email", "cv-" + UUID.randomUUID().toString().substring(0, 8) + "@test.com",
                "activo", true
        );
        return ((Number) restTemplate.exchange(
                url("/api/v1/clientes"), HttpMethod.POST,
                new HttpEntity<>(payload, authHeaders()), MAP_TYPE)
                .getBody().get("id")).longValue();
    }

    private Map<String, Object> ventaPayload(Long plantaId, Long clienteId) {
        return Map.of(
                "numeroFactura", "FAC-" + UUID.randomUUID().toString().substring(0, 8),
                "cantidad", 10,
                "precioUnitario", 1.80,
                "total", 18.00,
                "estado", "PENDIENTE",
                "fecha", "2026-05-01T10:00:00",
                "planta", Map.of("id", plantaId),
                "cliente", Map.of("id", clienteId)
        );
    }

    private ResponseEntity<Map<String, Object>> postVenta() {
        return restTemplate.exchange(
                url("/api/v1/ventas"), HttpMethod.POST,
                new HttpEntity<>(ventaPayload(createPlantaWithZona(), createCliente()), authHeaders()),
                MAP_TYPE);
    }

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/ventas"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/ventas"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void create_returnsCreated() {
        ResponseEntity<Map<String, Object>> r = postVenta();
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody()).containsKey("id");
    }

    @Test
    void getById_returnsVenta() {
        Long id = ((Number) postVenta().getBody().get("id")).longValue();
        ResponseEntity<String> found = restTemplate.exchange(
                url("/api/v1/ventas/" + id), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(found.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/ventas/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
