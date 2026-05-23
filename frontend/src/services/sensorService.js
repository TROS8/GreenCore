import api from '../api/axiosInstance'

const resourceUrl = '/sensores'

export function getAllSensors() {
  return api.get(resourceUrl).then((r) => r.data)
}

export function getSensor(id) {
  return api.get(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function createSensor(payload) {
  return api.post(resourceUrl, payload).then((r) => r.data)
}

export function updateSensor(id, payload) {
  return api.put(`${resourceUrl}/${id}`, payload).then((r) => r.data)
}

export function deleteSensor(id) {
  return api.delete(`${resourceUrl}/${id}`).then((r) => r.data)
}

export function registrarLectura(id, valor) {
  return api.post(`${resourceUrl}/${id}/lectura`, { valor }).then((r) => r.data)
}
