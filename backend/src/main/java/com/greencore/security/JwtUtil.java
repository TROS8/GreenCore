package com.greencore.security;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTVerificationException;
import com.auth0.jwt.interfaces.DecodedJWT;
import com.auth0.jwt.interfaces.JWTVerifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.Map;

@Component
public class JwtUtil {

    private final Algorithm algorithm;
    private final JWTVerifier verifier;
    private final long expirationHours;

    public JwtUtil(@Value("${app.jwt.secret}") String secret,
                   @Value("${app.jwt.expiration-hours}") long expirationHours) {
        this.algorithm = Algorithm.HMAC256(secret);
        this.verifier = JWT.require(algorithm).build();
        this.expirationHours = expirationHours;
    }

    public String generateToken(String email, String role) {
        Instant now = Instant.now();
        return JWT.create()
                .withSubject(email)
                .withClaim("role", role)
                .withIssuedAt(Date.from(now))
                .withExpiresAt(Date.from(now.plus(expirationHours, ChronoUnit.HOURS)))
                .sign(algorithm);
    }

    public DecodedJWT validateToken(String token) {
        try {
            return verifier.verify(token);
        } catch (JWTVerificationException e) {
            return null;
        }
    }

    public Map<String, Object> getClaims(String token) {
        DecodedJWT decodedJWT = validateToken(token);
        if (decodedJWT == null) {
            return Map.of();
        }
        return Map.of(
                "email", decodedJWT.getSubject(),
                "role", decodedJWT.getClaim("role").asString()
        );
    }
}
