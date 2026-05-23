import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/alertas`;

export function getAllAlertas() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getAlerta(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createAlerta(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateAlerta(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteAlerta(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}