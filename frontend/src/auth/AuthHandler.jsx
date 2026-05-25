/**
 * GreenCore — Sistema de gestion de invernadero
 * Lee el token JWT del parametro URL ?token=, lo persiste en Zustand
 * y extrae email y rol del payload para usarlos en la UI.
 *
 * @module auth/AuthHandler
 * @version 1.0.0
 */
import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useStore } from '../store/useStore'

export default function AuthHandler() {
  const { setToken } = useStore()
  const location     = useLocation()
  const navigate     = useNavigate()

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const token  = params.get('token')
    if (token) {
      setToken(token)          // setToken ya parsea el JWT y guarda role + user
      navigate('/', { replace: true })
    }
  }, [location.search])

  return null
}
