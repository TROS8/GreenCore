import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/clientes`;

export function getAllClientes() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getCliente(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createCliente(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateCliente(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteCliente(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}