/**
 * GreenCore — Sistema de gestion de invernadero
 * Guarda de ruta que redirige al login si no hay token JWT en el store.
 * Muestra una pagina de login con branding completo y soporte i18n.
 *
 * @module components/PrivateRoute
 * @version 2.0.0
 */
import React from 'react'
import { useTranslation } from 'react-i18next'
import { useStore } from '../store/useStore'

const LOGIN_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/oauth2/authorization/google`

const FEATURES = [
  { icon: '🌡️', key: 'feature1' },
  { icon: '📊', key: 'feature2' },
  { icon: '🔔', key: 'feature3' },
  { icon: '📋', key: 'feature4' },
]

export function PrivateRoute({ children }) {
  const { t } = useTranslation()
  const token          = useStore((s) => s.token)
  const sessionExpired = useStore((s) => s.sessionExpired)

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-950 to-slate-900 flex flex-col lg:flex-row">

        {/* ── Panel izquierdo: branding ───────────────────────────────────── */}
        <div className="hidden lg:flex flex-col justify-between w-1/2 px-16 py-14">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center shadow-lg">
              <span className="text-xl">🌿</span>
            </div>
            <span className="text-white text-xl font-bold tracking-tight">GreenCore</span>
          </div>

          {/* Eslogan */}
          <div className="space-y-6">
            <h1 className="text-5xl font-extrabold text-white leading-tight">
              {t('login.title')}
            </h1>
            <p className="text-emerald-300 text-lg leading-relaxed">
              {t('login.subtitle')}
            </p>

            {/* Feature list */}
            <ul className="space-y-4 mt-8">
              {FEATURES.map(({ icon, key }) => (
                <li key={key} className="flex items-start gap-4">
                  <div className="w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500/30
                                  flex items-center justify-center shrink-0 text-lg mt-0.5">
                    {icon}
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">{t(`login.${key}Title`)}</p>
                    <p className="text-slate-400 text-sm">{t(`login.${key}Desc`)}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Footer branding */}
          <p className="text-slate-600 text-xs">© {new Date().getFullYear()} GreenCore</p>
        </div>

        {/* ── Panel derecho: formulario ───────────────────────────────────── */}
        <div className="flex-1 flex items-center justify-center px-6 py-16 lg:py-0">
          <div className="w-full max-w-md">

            {/* Logo mobile */}
            <div className="flex lg:hidden items-center gap-3 mb-10 justify-center">
              <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center shadow-lg">
                <span className="text-xl">🌿</span>
              </div>
              <span className="text-white text-xl font-bold tracking-tight">GreenCore</span>
            </div>

            {/* Card */}
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl space-y-6">

              {/* Título */}
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-white">{t('login.title')}</h2>
                <p className="text-slate-400 text-sm">{t('login.subtitle')}</p>
              </div>

              {/* Banner sesión expirada */}
              {sessionExpired && (
                <div className="bg-amber-500/10 border border-amber-400/30 rounded-2xl px-4 py-3 space-y-1">
                  <p className="text-amber-300 font-semibold text-sm">
                    ⏱ {t('login.sessionExpiredTitle')}
                  </p>
                  <p className="text-amber-400/80 text-xs leading-relaxed">
                    {t('login.sessionExpiredDetail')}
                  </p>
                </div>
              )}

              {/* Mensaje de necesidad de login */}
              {!sessionExpired && (
                <p className="text-slate-400 text-sm text-center leading-relaxed">
                  {t('login.needsLogin')}
                </p>
              )}

              {/* Botón Google */}
              <a
                href={LOGIN_URL}
                className="group flex items-center justify-center gap-3 w-full
                           bg-white hover:bg-slate-50 text-slate-800
                           rounded-2xl px-6 py-3.5 font-semibold text-sm
                           shadow-lg hover:shadow-xl transition-all duration-200
                           border border-white/20 hover:scale-[1.02] active:scale-[0.98]"
              >
                {/* Google SVG icon */}
                <svg width="20" height="20" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path fill="#EA4335" d="M24 9.5c3.2 0 5.9 1.1 8.1 2.9l6-6C34.5 3.1 29.6 1 24 1 14.9 1 7.1 6.6 3.8 14.4l7 5.4C12.4 13.6 17.7 9.5 24 9.5z"/>
                  <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.4 5.7c4.3-4 6.8-9.9 6.8-16.9z"/>
                  <path fill="#FBBC05" d="M10.8 28.6A14.6 14.6 0 0 1 9.5 24c0-1.6.3-3.2.7-4.6l-7-5.4A23.9 23.9 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8l8.2-6.2z"/>
                  <path fill="#34A853" d="M24 47c5.8 0 10.7-1.9 14.3-5.2l-7.4-5.7c-1.9 1.3-4.4 2.1-6.9 2.1-6.3 0-11.6-4.1-13.2-9.8l-8.2 6.2C7.1 41.4 14.9 47 24 47z"/>
                </svg>
                {t('login.cta')}
              </a>

              {/* Feature pills — mobile only */}
              <div className="flex flex-wrap gap-2 justify-center lg:hidden pt-2">
                {FEATURES.map(({ icon, key }) => (
                  <span key={key}
                    className="inline-flex items-center gap-1.5 text-xs text-slate-400
                               bg-white/5 border border-white/10 rounded-full px-3 py-1">
                    {icon} {t(`login.${key}Title`)}
                  </span>
                ))}
              </div>
            </div>

            <p className="text-slate-600 text-xs text-center mt-6">© {new Date().getFullYear()} GreenCore</p>
          </div>
        </div>
      </div>
    )
  }

  return children
}
