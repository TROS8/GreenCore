/**
 * GreenCore — Sistema de gestion de invernadero
 * Servicio HTTP para la entidad Cliente. Consume /api/v1/clientes.
 *
 * @module services/clienteService
 * @version 1.0.0
 */
import api from '../api/axiosInstance'

const resourceUrl = '/clientes'

export function getAllClientes() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getCliente(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function createCliente(payload) {
  return api.post(resourceUrl, payload).then((r) => r.data)
}

export function updateCliente(id, payload) {
  return api.put(`${resourceUrl}/${id}`, payload).then((r) => r.data)
}

export function deleteCliente(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}
