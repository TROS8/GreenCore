import api from '../api/axiosInstance'

const resourceUrl = '/usuarios'

export function getAllUsuarios() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getUsuario(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function updateUsuario(id, payload) {
  return api.put(`${resourceUrl}/${id}`, payload).then((r) => r.data)
}

export function deleteUsuario(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}
