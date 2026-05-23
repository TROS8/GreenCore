/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio HTTP para la entidad Alerta. Consume /api/v1/alertas.
 *
 * @module services/alertaService
 * @version 1.0.0
 */
import api from '../api/axiosInstance'

const resourceUrl = '/alertas'

export function getAllAlertas() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getAlerta(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function getAlertasNoLeidas() {
  return api.get(`${resourceUrl}/no-leidas`).then((r) => r.data)
}

export function marcarLeida(id) {
  return api.patch(`${resourceUrl}/${id}/leer`).then((r) => r.data)
}

export function deleteAlerta(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}
