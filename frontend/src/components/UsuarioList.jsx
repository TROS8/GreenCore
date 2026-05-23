import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllUsuarios } from '../services/usuarioService'

export function UsuarioList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAllUsuarios().then(setItems).finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">{t('usuario.title')}</h2>
      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((u) => (
            <div key={u.id} className="border rounded-lg p-4 bg-slate-50 flex items-center gap-3">
              {u.fotoPerfil ? (
                <img src={u.fotoPerfil} alt={u.nombre} className="w-10 h-10 rounded-full object-cover" />
              ) : (
                <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700 font-bold text-sm">
                  {u.nombre?.[0]?.toUpperCase()}
                </div>
              )}
              <div>
                <p className="font-semibold text-sm">{u.nombre}</p>
                <p className="text-xs text-slate-500">{u.email}</p>
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 mt-1 inline-block">
                  {u.rol}
                </span>
              </div>
            </div>
          ))}
          {items.length === 0 && <p className="text-slate-400 text-sm">Sin usuarios registrados.</p>}
        </div>
      )}
    </div>
  )
}
