import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/plantas`;

export function getAllPlantas() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getPlanta(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createPlanta(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updatePlanta(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deletePlanta(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}