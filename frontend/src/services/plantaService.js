/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio HTTP para la entidad Planta. Consume /api/v1/plantas.
 *
 * @module services/plantaService
 * @version 1.0.0
 */
import api from '../api/axiosInstance'

const resourceUrl = '/plantas'

export function getAllPlantas() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getPlanta(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function getPlantasByZona(zonaId) {
  return api.get(`${resourceUrl}/zona/${zonaId}`).then((r) => r.data)
}

export function createPlanta(payload) {
  return api.post(resourceUrl, payload).then((r) => r.data)
}

export function updatePlanta(id, payload) {
  return api.put(`${resourceUrl}/${id}`, payload).then((r) => r.data)
}

export function deletePlanta(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}
