package com.greencore;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

public class TestTokenHelper {

    public static final String TEST_SECRET = "test-jwt-secret-for-junit-only";

    public static String generate() {
        Instant now = Instant.now();
        return JWT.create()
                .withSubject("testuser@greencore.test")
                .withClaim("role", "ADMIN")
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(now.plus(24, ChronoUnit.HOURS)))
                .sign(Algorithm.HMAC256(TEST_SECRET));
    }
}
