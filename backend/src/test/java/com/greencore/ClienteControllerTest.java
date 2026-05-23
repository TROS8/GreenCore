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
class ClienteControllerTest {

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

    private Map<String, Object> clientePayload() {
        return Map.of(
                "nombre", "Cliente Test",
                "email", "cli-" + UUID.randomUUID().toString().substring(0, 8) + "@test.com",
                "telefono", "555-0100",
                "ciudad", "Lima",
                "activo", true
        );
    }

    private ResponseEntity<Map<String, Object>> postCliente() {
        return restTemplate.exchange(
                url("/api/v1/clientes"), HttpMethod.POST,
                new HttpEntity<>(clientePayload(), authHeaders()), MAP_TYPE);
    }

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/clientes"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/clientes"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void create_returnsCreated() {
        ResponseEntity<Map<String, Object>> r = postCliente();
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(r.getBody()).containsKey("id");
    }

    @Test
    void getById_returnsCliente() {
        Long id = ((Number) postCliente().getBody().get("id")).longValue();
        ResponseEntity<String> found = restTemplate.exchange(
                url("/api/v1/clientes/" + id), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(found.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/clientes/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void delete_returnsNoContent() {
        Long id = ((Number) postCliente().getBody().get("id")).longValue();
        ResponseEntity<Void> deleted = restTemplate.exchange(
                url("/api/v1/clientes/" + id), HttpMethod.DELETE,
                new HttpEntity<>(authHeaders()), Void.class);
        assertThat(deleted.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);
    }
}
