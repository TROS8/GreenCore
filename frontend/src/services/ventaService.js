import api from '../api/axiosInstance'

const resourceUrl = '/ventas'

export function getAllVentas() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getVenta(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function getVentasByCliente(clienteId) {
  return api.get(`${resourceUrl}/cliente/${clienteId}`).then((r) => r.data)
}

export function getVentasByFecha(from, to) {
  return api.get(resourceUrl, { params: { from, to } }).then((r) => r.data)
}

export function createVenta(payload) {
  return api.post(resourceUrl, payload).then((r) => r.data)
}
