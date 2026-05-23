import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/usuarios`;

export function getAllUsuarios() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getUsuario(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createUsuario(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateUsuario(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteUsuario(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}