/**
 * GreenCore — Sistema de gestion de invernadero
 * Barra de navegacion principal. Muestra enlaces filtrados por rol,
 * badge de rol, avatar del usuario y boton de logout.
 *
 * @module components/Navbar
 * @version 1.0.0
 */
import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useStore } from '../store/useStore'

const ALL_LINKS = [
  { to: '/',         key: 'nav.dashboard', roles: ['ADMIN','OPERARIO','VISUALIZADOR'] },
  { to: '/zonas',    key: 'nav.zonas',     roles: ['ADMIN','OPERARIO','VISUALIZADOR'] },
  { to: '/plantas',  key: 'nav.plantas',   roles: ['ADMIN','OPERARIO','VISUALIZADOR'] },
  { to: '/sensores', key: 'nav.sensores',  roles: ['ADMIN','OPERARIO','VISUALIZADOR'] },
  { to: '/alertas',  key: 'nav.alertas',   roles: ['ADMIN','OPERARIO','VISUALIZADOR'] },
  { to: '/clientes', key: 'nav.clientes',  roles: ['ADMIN','OPERARIO'] },
  { to: '/ventas',   key: 'nav.ventas',    roles: ['ADMIN','OPERARIO'] },
  { to: '/usuarios', key: 'nav.usuarios',  roles: ['ADMIN','OPERARIO'] },
]

const ROLE_BADGE = {
  ADMIN:       'bg-red-500 text-white',
  OPERARIO:    'bg-blue-500 text-white',
  VISUALIZADOR:'bg-slate-500 text-white',
}

const ROLE_LABEL = {
  ADMIN:       'Admin',
  OPERARIO:    'Operario',
  VISUALIZADOR:'Visualizador',
}

export default function Navbar() {
  const { t, i18n } = useTranslation()
  const { token, user, role, logout, locale, setLocale } = useStore()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const toggleLocale = () => {
    const next = locale === 'es' ? 'en' : 'es'
    setLocale(next)
    i18n.changeLanguage(next)
  }

  const visibleLinks = ALL_LINKS.filter(l => !role || l.roles.includes(role))

  return (
    <nav className="bg-gradient-to-r from-emerald-800 to-emerald-700 text-white shadow-lg">
      {/* Barra principal */}
      <div className="flex items-center gap-2 px-4 py-3">

        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2 font-bold text-lg shrink-0 mr-2">
          <span className="text-2xl">🌿</span>
          <span className="hidden sm:inline tracking-tight">GreenCore</span>
        </NavLink>

        {/* Links — desktop */}
        <div className="hidden lg:flex items-center gap-0.5 flex-1 overflow-x-auto">
          {visibleLinks.map(({ to, key }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition-all duration-150
                 ${isActive
                   ? 'bg-emerald-900 text-white shadow-sm'
                   : 'text-emerald-100 hover:bg-emerald-600 hover:text-white'}`
              }
            >
              {t(key)}
            </NavLink>
          ))}
        </div>

        {/* Lado derecho */}
        <div className="ml-auto flex items-center gap-2 shrink-0">

          {/* Toggle idioma */}
          <button
            onClick={toggleLocale}
            className="text-xs px-2.5 py-1 rounded-md bg-white/10 hover:bg-white/20 uppercase font-semibold transition"
            title="Cambiar idioma"
          >
            {locale === 'es' ? 'EN' : 'ES'}
          </button>

          {token ? (
            <div className="flex items-center gap-2">
              {/* Badge de rol */}
              {role && (
                <span className={`hidden sm:inline text-xs px-2 py-0.5 rounded-full font-semibold ${ROLE_BADGE[role] || 'bg-slate-500 text-white'}`}>
                  {ROLE_LABEL[role] || role}
                </span>
              )}

              {/* Info del usuario */}
              {user && (
                <span className="hidden md:inline text-xs text-emerald-200 truncate max-w-[140px]">
                  {user.nombre || user.email}
                </span>
              )}

              {/* Botón logout */}
              <button
                onClick={handleLogout}
                className="text-xs px-3 py-1.5 rounded-md bg-white/10 hover:bg-red-500 transition-all duration-150 font-medium"
              >
                {t('nav.logout')}
              </button>
            </div>
          ) : (
            <a
              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/oauth2/authorization/google`}
              className="text-xs px-3 py-1.5 rounded-md bg-white text-emerald-800 font-bold hover:bg-emerald-50 transition shadow-sm"
            >
              {t('nav.login')}
            </a>
          )}

          {/* Menú hamburguesa — mobile */}
          <button
            className="lg:hidden p-1.5 rounded hover:bg-white/10 transition"
            onClick={() => setMenuOpen(o => !o)}
            aria-label="Menú"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen
                ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              }
            </svg>
          </button>
        </div>
      </div>

      {/* Menú desplegable mobile */}
      {menuOpen && (
        <div className="lg:hidden border-t border-emerald-600 px-3 py-2 flex flex-col gap-1">
          {visibleLinks.map(({ to, key }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={() => setMenuOpen(false)}
              className={({ isActive }) =>
                `px-3 py-2 rounded-md text-sm font-medium transition
                 ${isActive ? 'bg-emerald-900' : 'hover:bg-emerald-600'}`
              }
            >
              {t(key)}
            </NavLink>
          ))}
        </div>
      )}
    </nav>
  )
}
