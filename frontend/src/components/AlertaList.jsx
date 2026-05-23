/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista de alertas automaticas. Permite marcar alertas como leidas.
 *
 * @module components/AlertaList
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllAlertas, marcarLeida } from '../services/alertaService'

const nivelColor = {
  INFO: 'bg-blue-50 border-blue-200 text-blue-700',
  ADVERTENCIA: 'bg-yellow-50 border-yellow-300 text-yellow-700',
  CRITICO: 'bg-red-50 border-red-300 text-red-700',
}

export function AlertaList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAllAlertas().then(setItems).finally(() => setLoading(false))
  }, [])

  const handleMarcarLeida = (id) => {
    marcarLeida(id).then(() =>
      setItems((prev) => prev.map((a) => (a.id === id ? { ...a, leida: true } : a)))
    )
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">{t('alerta.title')}</h2>
      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="space-y-3">
          {items.map((a) => (
            <div
              key={a.id}
              className={`border rounded-lg p-4 ${nivelColor[a.nivel] || 'bg-slate-50 border-slate-200'} ${a.leida ? 'opacity-60' : ''}`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-semibold text-sm uppercase tracking-wide">{a.nivel}</span>
                  <p className="text-sm mt-1">{a.mensaje}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {new Date(a.timestamp).toLocaleString()} · Valor: {a.valorRegistrado}
                  </p>
                </div>
                {!a.leida && (
                  <button
                    onClick={() => handleMarcarLeida(a.id)}
                    className="text-xs px-3 py-1 bg-white rounded border border-current ml-4 hover:opacity-80 shrink-0"
                  >
                    Marcar leída
                  </button>
                )}
              </div>
            </div>
          ))}
          {items.length === 0 && <p className="text-slate-400 text-sm">Sin alertas registradas.</p>}
        </div>
      )}
    </div>
  )
}
