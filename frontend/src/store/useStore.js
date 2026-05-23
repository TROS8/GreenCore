import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      locale: 'es',
      sessionExpired: false,
      setToken: (token) => set({ token, sessionExpired: false }),
      setUser: (user) => set({ user }),
      setLocale: (locale) => set({ locale }),
      logout: () => set({ token: null, user: null, sessionExpired: false }),
      expireSession: () => set({ token: null, user: null, sessionExpired: true }),
    }),
    {
      name: 'greencore-store',
      partialize: (state) => ({ token: state.token, user: state.user, locale: state.locale }),
    }
  )
)
