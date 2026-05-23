package com.greencore.security;

import com.greencore.model.Usuario;
import com.greencore.service.UsuarioService;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Map;

@Component
public class OAuth2SuccessHandler implements AuthenticationSuccessHandler {

    private final JwtUtil jwtUtil;
    private final UsuarioService usuarioService;
    private final String frontendUrl;

    public OAuth2SuccessHandler(JwtUtil jwtUtil,
                                UsuarioService usuarioService,
                                @Value("${app.frontend-url}") String frontendUrl) {
        this.jwtUtil = jwtUtil;
        this.usuarioService = usuarioService;
        this.frontendUrl = frontendUrl;
    }

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request,
                                        HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {
        var oidcUser = (OidcUser) authentication.getPrincipal();
        String email = oidcUser.getEmail();
        String name = oidcUser.getFullName();
        String picture = oidcUser.getPicture();
        String providerId = oidcUser.getSubject();

        Usuario usuario = usuarioService.upsertGoogleUser(email, name, picture, providerId);
        String token = jwtUtil.generateToken(usuario.getEmail(), usuario.getRol().name());
        String redirectUrl = frontendUrl + "/?token=" + URLEncoder.encode(token, StandardCharsets.UTF_8);

        response.sendRedirect(redirectUrl);
    }
}
