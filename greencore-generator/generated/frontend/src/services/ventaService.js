import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/ventas`;

export function getAllVentas() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getVenta(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createVenta(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateVenta(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteVenta(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}