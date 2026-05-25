/**
 * GreenCore — Sistema de gestion de invernadero
 * Store global de Zustand con persistencia en localStorage.
 * Gestiona token, usuario, rol e idioma.
 *
 * @module store/useStore
 * @version 1.0.0
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/** Decodifica el payload de un JWT sin libreria externa. */
function parseJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return {}
  }
}

export const useStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      role: null,        // 'ADMIN' | 'OPERARIO' | 'VISUALIZADOR'
      locale: 'es',
      sessionExpired: false,

      setToken: (token) => {
        const payload = parseJwtPayload(token)
        set({
          token,
          role: payload.role || null,
          user: payload.sub  ? { email: payload.sub, ...(payload.name ? { nombre: payload.name } : {}) } : null,
          sessionExpired: false,
        })
      },

      setUser:   (user)   => set({ user }),
      setLocale: (locale) => set({ locale }),

      logout: () => set({ token: null, user: null, role: null, sessionExpired: false }),
      expireSession: () => set({ token: null, user: null, role: null, sessionExpired: true }),
    }),
    {
      name: 'greencore-store',
      partialize: (state) => ({
        token:  state.token,
        user:   state.user,
        role:   state.role,
        locale: state.locale,
      }),
    }
  )
)
