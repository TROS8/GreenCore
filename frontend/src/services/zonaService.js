/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio HTTP para la entidad Zona. Consume /api/v1/zonas.
 *
 * @module services/zonaService
 * @version 1.0.0
 */
import api from '../api/axiosInstance'

const resourceUrl = '/zonas'

export function getAllZonas() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getZona(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function createZona(payload) {
  return api.post(resourceUrl, payload).then((r) => r.data)
}

export function updateZona(id, payload) {
  return api.put(`${resourceUrl}/${id}`, payload).then((r) => r.data)
}

export function deleteZona(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}
