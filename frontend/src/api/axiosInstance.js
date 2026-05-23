import axios from 'axios'
import { useStore } from '../store/useStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = useStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only expire session if we actually had a token (not a race on cold load)
      if (useStore.getState().token) {
        useStore.getState().expireSession()
      }
    }
    return Promise.reject(error)
  }
)

export default api
