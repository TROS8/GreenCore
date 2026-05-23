/**
 * GreenCore — Sistema de gestion de invernadero
 * Guarda de ruta que redirige al login si no hay token JWT en el store.
 *
 * @module components/PrivateRoute
 * @version 1.0.0
 */
import React from 'react'
import { useStore } from '../store/useStore'

const LOGIN_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/oauth2/authorization/google`

export function PrivateRoute({ children }) {
  const token = useStore((s) => s.token)
  const sessionExpired = useStore((s) => s.sessionExpired)

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-4">
        <div className="text-5xl">🌿</div>
        {sessionExpired ? (
          <>
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-6 py-4 max-w-sm">
              <p className="text-amber-800 font-semibold text-base">Sesión expirada</p>
              <p className="text-amber-700 text-sm mt-1">Tu sesión venció o el servidor fue reiniciado. Por favor, inicia sesión de nuevo.</p>
            </div>
          </>
        ) : (
          <p className="text-slate-600 text-lg font-medium">Debes iniciar sesión para acceder a esta sección.</p>
        )}
        <a
          href={LOGIN_URL}
          className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
        >
          Iniciar sesión con Google
        </a>
      </div>
    )
  }

  return children
}
