import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const resourceUrl = `${BASE_URL}/sensores`;

export function getAllSensors() {
  return axios.get(resourceUrl).then((response) => response.data);
}

export function getSensor(id) {
  return axios.get(`${resourceUrl}/${id}`).then((response) => response.data);
}

export function createSensor(payload) {
  return axios.post(resourceUrl, payload).then((response) => response.data);
}

export function updateSensor(id, payload) {
  return axios.put(`${resourceUrl}/${id}`, payload).then((response) => response.data);
}

export function deleteSensor(id) {
  return axios.delete(`${resourceUrl}/${id}`).then((response) => response.data);
}