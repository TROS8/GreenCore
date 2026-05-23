/**
 * GreenCore — Sistema de gestion de invernadero
 * Barra de navegacion principal. Muestra enlaces, toggle de idioma y boton de logout.
 *
 * @module components/Navbar
 * @version 1.0.0
 */
import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useStore } from '../store/useStore'

const links = [
  { to: '/',         key: 'nav.dashboard' },
  { to: '/zonas',    key: 'nav.zonas' },
  { to: '/plantas',  key: 'nav.plantas' },
  { to: '/sensores', key: 'nav.sensores' },
  { to: '/alertas',  key: 'nav.alertas' },
  { to: '/clientes', key: 'nav.clientes' },
  { to: '/ventas',   key: 'nav.ventas' },
  { to: '/usuarios', key: 'nav.usuarios' },
]

export default function Navbar() {
  const { t, i18n } = useTranslation()
  const { token, user, logout, locale, setLocale } = useStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const toggleLocale = () => {
    const next = locale === 'es' ? 'en' : 'es'
    setLocale(next)
    i18n.changeLanguage(next)
  }

  return (
    <nav className="bg-emerald-700 text-white flex items-center gap-1 px-4 py-2 flex-wrap">
      <span className="font-bold text-lg mr-4">🌿 GreenCore</span>

      {links.map(({ to, key }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `px-3 py-1 rounded text-sm transition-colors ${isActive ? 'bg-emerald-900' : 'hover:bg-emerald-600'}`
          }
        >
          {t(key)}
        </NavLink>
      ))}

      <div className="ml-auto flex items-center gap-3">
        <button
          onClick={toggleLocale}
          className="text-xs px-2 py-1 rounded bg-emerald-600 hover:bg-emerald-500 uppercase"
        >
          {locale === 'es' ? 'EN' : 'ES'}
        </button>

        {token ? (
          <button
            onClick={handleLogout}
            className="text-xs px-3 py-1 rounded bg-emerald-600 hover:bg-red-600 transition-colors"
          >
            {t('nav.logout')}
          </button>
        ) : (
          <a
            href={`${import.meta.env.VITE_API_URL || 'http://localhost:8080'}/oauth2/authorization/google`}
            className="text-xs px-3 py-1 rounded bg-white text-emerald-700 font-semibold hover:bg-emerald-50"
          >
            {t('nav.login')}
          </a>
        )}
      </div>
    </nav>
  )
}
