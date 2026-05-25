/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio de logica de negocio para Venta. Gestiona stock y facturacion automatica.
 * <p>
 * Al crear una venta:
 * <ul>
 *   <li>Valida que el stock de la planta sea suficiente.</li>
 *   <li>Genera automaticamente el numero de factura con patron FAC-{AÑO}-{SEQ}.</li>
 *   <li>Calcula {@code precioUnitario} y {@code total} desde el precio de la planta.</li>
 *   <li>Descuenta el stock de la planta; si llega a 0, cambia su estado a VENDIDA.</li>
 * </ul>
 * Al anular una venta (estado → ANULADA), restaura el stock automaticamente.
 * </p>
 *
 * @author GreenCore Team
 * @version 1.0.0
 */
package com.greencore.service;

import com.greencore.model.EstadoPlanta;
import com.greencore.model.EstadoVenta;
import com.greencore.model.Planta;
import com.greencore.model.Venta;
import com.greencore.repository.PlantaRepository;
import com.greencore.repository.VentaRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class VentaService {

    private final VentaRepository repository;
    private final PlantaRepository plantaRepository;

    /**
     * @param repository      repositorio JPA de ventas
     * @param plantaRepository repositorio JPA de plantas (para control de stock)
     */
    public VentaService(VentaRepository repository, PlantaRepository plantaRepository) {
        this.repository = repository;
        this.plantaRepository = plantaRepository;
    }

    /** Retorna todas las ventas registradas. */
    public List<Venta> findAll() {
        return repository.findAll();
    }

    /** Filtra ventas por cliente. */
    public List<Venta> findByClienteId(Long clienteId) {
        return repository.findByClienteId(clienteId);
    }

    /** Filtra ventas por rango de fechas. */
    public List<Venta> findByFechaBetween(LocalDateTime from, LocalDateTime to) {
        return repository.findByFechaBetween(from, to);
    }

    /** Busca una venta por ID. */
    public Optional<Venta> findById(Long id) {
        return repository.findById(id);
    }

    /**
     * Crea o actualiza una venta aplicando logica de negocio completa.
     * <ul>
     *   <li>Si {@code entity.getId() == null}: nueva venta con validacion de stock.</li>
     *   <li>Si {@code entity.getId() != null}: actualizacion; si cambia a ANULADA restaura stock.</li>
     * </ul>
     *
     * @param entity datos de la venta
     * @return venta persistida
     * @throws ResponseStatusException HTTP 400 si el stock es insuficiente
     * @throws ResponseStatusException HTTP 404 si la planta no existe
     */
    public Venta save(Venta entity) {
        if (entity.getId() == null) {
            return crearVenta(entity);
        } else {
            return actualizarVenta(entity);
        }
    }

    /**
     * Elimina una venta por ID.
     *
     * @param id identificador de la venta a eliminar
     */
    public void delete(Long id) {
        repository.deleteById(id);
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Metodos privados de negocio
    // ──────────────────────────────────────────────────────────────────────────

    /**
     * Logica de creacion: valida stock, genera numero de factura, descuenta inventario.
     *
     * @param entity nueva venta sin ID
     * @return venta persistida con todos los campos calculados
     */
    private Venta crearVenta(Venta entity) {
        // 1 ── Cargar planta con datos completos
        Long plantaId = entity.getPlanta() == null ? null : entity.getPlanta().getId();
        Planta planta = plantaRepository.findById(plantaId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Planta no encontrada con ID: " + plantaId));

        // 2 ── Validar stock suficiente
        int solicitado = entity.getCantidad() == null ? 0 : entity.getCantidad();
        if (planta.getCantidad() < solicitado) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "Stock insuficiente. Disponible: " + planta.getCantidad()
                    + ", solicitado: " + solicitado);
        }

        // 3 ── Generar numero de factura: FAC-{AÑO}-{SEQ:0000}
        int year = LocalDateTime.now().getYear();
        String prefix = "FAC-" + year + "-";
        long seq = repository.countByNumeroFacturaStartingWith(prefix) + 1;
        entity.setNumeroFactura(prefix + String.format("%04d", seq));

        // 4 ── Precio unitario y total calculados desde la planta
        entity.setPrecioUnitario(planta.getPrecio());
        entity.setTotal(planta.getPrecio().multiply(BigDecimal.valueOf(solicitado)));

        // 5 ── Timestamp de la venta
        entity.setFecha(LocalDateTime.now());

        // 6 ── Descontar stock; marcar VENDIDA si llega a 0
        planta.setCantidad(planta.getCantidad() - solicitado);
        if (planta.getCantidad() == 0) {
            planta.setEstado(EstadoPlanta.VENDIDA);
        }
        plantaRepository.save(planta);

        return repository.save(entity);
    }

    /**
     * Logica de actualizacion: si el estado cambia a ANULADA, restaura el stock de la planta.
     *
     * @param entity venta con ID existente y nuevos datos
     * @return venta actualizada
     */
    private Venta actualizarVenta(Venta entity) {
        Venta existente = repository.findById(entity.getId())
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Venta no encontrada con ID: " + entity.getId()));

        // Si la venta pasa a ANULADA, restaurar stock
        boolean anulandoAhora = EstadoVenta.ANULADA.equals(entity.getEstado())
                && !EstadoVenta.ANULADA.equals(existente.getEstado());

        if (anulandoAhora && existente.getPlanta() != null) {
            plantaRepository.findById(existente.getPlanta().getId()).ifPresent(planta -> {
                planta.setCantidad(planta.getCantidad() + existente.getCantidad());
                // Si estaba marcada como vendida, volver a LISTA_VENTA
                if (EstadoPlanta.VENDIDA.equals(planta.getEstado())) {
                    planta.setEstado(EstadoPlanta.LISTA_VENTA);
                }
                plantaRepository.save(planta);
            });
        }

        // Preservar campos de solo lectura del registro original
        entity.setNumeroFactura(existente.getNumeroFactura());
        entity.setPrecioUnitario(existente.getPrecioUnitario());
        entity.setTotal(existente.getTotal());
        entity.setFecha(existente.getFecha());

        return repository.save(entity);
    }
}
