import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/zonas`;

export function getAllZonas() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getZona(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createZona(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateZona(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteZona(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}