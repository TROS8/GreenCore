/**
 * GreenCore — Sistema de gestion de invernadero
 * Lee el token JWT del parametro URL ?token= y lo persiste en el store de Zustand.
 *
 * @module auth/AuthHandler
 * @version 1.0.0
 */
import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function AuthHandler() {
  const { setToken } = useStore()
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const token = params.get('token')
    if (token) {
      setToken(token)
      navigate('/', { replace: true })
    }
  }, [location.search])

  return null
}
