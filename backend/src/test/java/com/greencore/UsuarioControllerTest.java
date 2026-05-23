package com.greencore;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.*;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
class UsuarioControllerTest {

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

    @Test
    void contextLoads() {
        assertThat(port).isGreaterThan(0);
    }

    @Test
    void unauthorizedRequest_returns401() {
        assertThat(restTemplate.getForEntity(url("/api/v1/usuarios"), String.class)
                .getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void getAll_withAuth_returnsOk() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/usuarios"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode().is2xxSuccessful()).isTrue();
    }

    @Test
    void getById_notFound_returns404() {
        ResponseEntity<String> r = restTemplate.exchange(
                url("/api/v1/usuarios/999999"), HttpMethod.GET,
                new HttpEntity<>(authHeaders()), String.class);
        assertThat(r.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }
}
