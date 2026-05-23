/**
 * GreenCore — Sistema de gestión de invernadero
 * Configuración de internacionalización (i18n) para Spring MVC.
 * Registra el LocaleResolver y el MessageSource que leen los archivos
 * messages.properties (ES) y messages_en.properties (EN), generados
 * automáticamente desde modelo.json por greencore-generator.
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.config;

import org.springframework.context.MessageSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.support.ReloadableResourceBundleMessageSource;
import org.springframework.web.servlet.LocaleResolver;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.i18n.AcceptHeaderLocaleResolver;
import org.springframework.web.servlet.i18n.LocaleChangeInterceptor;

import java.util.List;
import java.util.Locale;

/**
 * Configura la internacionalización del backend GreenCore.
 *
 * <p>El idioma se resuelve automáticamente a partir de la cabecera HTTP
 * {@code Accept-Language} enviada por el cliente.  Si no se especifica, o si
 * el idioma no está soportado, se usa español ({@code es}) como fallback.</p>
 *
 * <p>Idiomas soportados: {@code es} (español), {@code en} (inglés).</p>
 *
 * <p>Los archivos de mensajes son generados automáticamente desde
 * {@code modelo.json} por el script {@code greencore-generator/generate.py}.
 * No editar manualmente.</p>
 */
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    /** Locale por defecto cuando no se especifica Accept-Language. */
    private static final Locale DEFAULT_LOCALE = new Locale("es");

    /** Locales soportados por el sistema. */
    private static final List<Locale> SUPPORTED_LOCALES = List.of(
            new Locale("es"),
            new Locale("en")
    );

    /**
     * Resuelve el locale de cada petición a partir de la cabecera
     * {@code Accept-Language}.
     *
     * <p>Ejemplo de uso desde el cliente:</p>
     * <pre>
     *   GET /api/v1/zonas
     *   Accept-Language: en
     * </pre>
     *
     * @return {@link AcceptHeaderLocaleResolver} configurado con idiomas soportados
     */
    @Bean
    public LocaleResolver localeResolver() {
        AcceptHeaderLocaleResolver resolver = new AcceptHeaderLocaleResolver();
        resolver.setDefaultLocale(DEFAULT_LOCALE);
        resolver.setSupportedLocales(SUPPORTED_LOCALES);
        return resolver;
    }

    /**
     * Carga los archivos de mensajes i18n desde {@code classpath:messages*.properties}.
     * Codificación UTF-8. Recarga automática en caliente si el archivo cambia.
     *
     * <p>Archivos generados automáticamente:</p>
     * <ul>
     *   <li>{@code messages.properties} — español (por defecto)</li>
     *   <li>{@code messages_en.properties} — inglés</li>
     * </ul>
     *
     * @return {@link MessageSource} configurado para i18n
     */
    @Bean
    public MessageSource messageSource() {
        ReloadableResourceBundleMessageSource ms = new ReloadableResourceBundleMessageSource();
        ms.setBasename("classpath:messages");
        ms.setDefaultEncoding("UTF-8");
        ms.setDefaultLocale(DEFAULT_LOCALE);
        ms.setUseCodeAsDefaultMessage(true);  // devuelve la clave si no hay traducción
        ms.setCacheSeconds(3600);             // recarga cada hora en producción
        return ms;
    }

    /**
     * Permite cambiar el idioma mediante el parámetro de URL {@code ?lang=en}.
     * Funciona complementando la cabecera Accept-Language.
     *
     * @return interceptor de cambio de locale
     */
    @Bean
    public LocaleChangeInterceptor localeChangeInterceptor() {
        LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
        interceptor.setParamName("lang");
        return interceptor;
    }

    /**
     * Registra el interceptor de cambio de locale en el pipeline de Spring MVC.
     *
     * @param registry registro de interceptores de Spring MVC
     */
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(localeChangeInterceptor());
    }
}
