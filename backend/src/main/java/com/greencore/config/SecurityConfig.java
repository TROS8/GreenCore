/**
 * GreenCore — Sistema de gestion de invernadero
 * Configuracion de Spring Security: JWT stateless, OAuth2 Google, CORS y rutas publicas.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.config;

import com.greencore.security.JwtFilter;
import com.greencore.security.OAuth2SuccessHandler;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestResolver;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtFilter jwtFilter;
    private final OAuth2SuccessHandler oAuth2SuccessHandler;
    private final ClientRegistrationRepository clientRegistrationRepository;

    @Value("${app.frontend-url:http://localhost:5173}")
    private String frontendUrl;

    public SecurityConfig(JwtFilter jwtFilter,
                          OAuth2SuccessHandler oAuth2SuccessHandler,
                          ClientRegistrationRepository clientRegistrationRepository) {
        this.jwtFilter = jwtFilter;
        this.oAuth2SuccessHandler = oAuth2SuccessHandler;
        this.clientRegistrationRepository = clientRegistrationRepository;
    }

    /**
     * Resolver personalizado que agrega prompt=select_account a cada solicitud OAuth2,
     * forzando a Google a mostrar el selector de cuentas en cada inicio de sesion.
     */
    @Bean
    public OAuth2AuthorizationRequestResolver authorizationRequestResolver() {
        DefaultOAuth2AuthorizationRequestResolver resolver =
                new DefaultOAuth2AuthorizationRequestResolver(
                        clientRegistrationRepository, "/oauth2/authorization");
        resolver.setAuthorizationRequestCustomizer(
                builder -> builder.additionalParameters(
                        params -> params.put("prompt", "select_account")));
        return resolver;
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of(frontendUrl));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .cors(Customizer.withDefaults())
                .headers(headers -> headers.cacheControl(Customizer.withDefaults()))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint((request, response, authException) -> {
                            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                            response.setContentType("application/json;charset=UTF-8");
                            response.getWriter().write("{\"error\":\"Token missing or expired. Please log in again.\"}");
                        })
                )
                .authorizeHttpRequests(authorize -> authorize
                        // ── Endpoints publicos ──────────────────────────────
                        .requestMatchers(
                                "/api/v1/auth/**",
                                "/swagger-ui/**",
                                "/v3/api-docs/**",
                                "/oauth2/**",
                                "/login/oauth2/**",
                                "/actuator/health",   // health-check para CI/CD
                                "/actuator/info"
                        ).permitAll()

                        // ── Gestion de usuarios: solo ADMIN puede borrar ───
                        .requestMatchers(HttpMethod.DELETE, "/api/v1/usuarios/**")
                                .hasRole("ADMIN")
                        // ADMIN y OPERARIO pueden ver usuarios
                        .requestMatchers(HttpMethod.GET, "/api/v1/usuarios/**")
                                .hasAnyRole("ADMIN", "OPERARIO")

                        // ── Operaciones de escritura: ADMIN + OPERARIO ─────
                        // VISUALIZADOR es de solo lectura
                        .requestMatchers(HttpMethod.POST,   "/api/v1/**")
                                .hasAnyRole("ADMIN", "OPERARIO")
                        .requestMatchers(HttpMethod.PUT,    "/api/v1/**")
                                .hasAnyRole("ADMIN", "OPERARIO")
                        .requestMatchers(HttpMethod.PATCH,  "/api/v1/**")
                                .hasAnyRole("ADMIN", "OPERARIO")
                        .requestMatchers(HttpMethod.DELETE, "/api/v1/**")
                                .hasAnyRole("ADMIN", "OPERARIO")

                        // ── Lectura: cualquier usuario autenticado ─────────
                        .anyRequest().authenticated()
                )
                .oauth2Login(oauth2 -> oauth2
                        .loginPage("/oauth2/authorization/google")
                        .authorizationEndpoint(authz -> authz
                                .authorizationRequestResolver(authorizationRequestResolver()))
                        .successHandler(oAuth2SuccessHandler)
                )
                .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
