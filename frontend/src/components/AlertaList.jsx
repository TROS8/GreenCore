/**
 * GreenCore — Vista de alertas automaticas.
 *
 * @module components/AlertaList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllAlertas, marcarLeida } from '../services/alertaService'
import { Spinner, EmptyState, PageHeader, ActionBtn } from './ui'

const NIVEL_STYLE = {
  INFO:        'border-blue-200   bg-blue-50   text-blue-700',
  ADVERTENCIA: 'border-yellow-300 bg-yellow-50 text-yellow-700',
  CRITICO:     'border-red-300    bg-red-50    text-red-700',
}

const NIVEL_ICON = {
  INFO: 'ℹ️',
  ADVERTENCIA: '⚠️',
  CRITICO: '🚨',
}

export function AlertaList() {
  const { t } = useTranslation()
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAllAlertas().then(setItems).finally(() => setLoading(false))
  }, [])

  const handleMarcarLeida = (id) => {
    marcarLeida(id).then(() =>
      setItems((prev) => prev.map((a) => (a.id === id ? { ...a, leida: true } : a)))
    )
  }

  const unread = items.filter((a) => !a.leida).length

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('alerta.title')}
        count={items.length}
      />

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="✅" message={t('alerta.noData')} />
      ) : (
        <div className="space-y-3">
          {unread > 0 && (
            <p className="text-xs text-slate-400 font-medium">
              {unread} {unread === 1 ? 'alerta sin leer' : 'alertas sin leer'}
            </p>
          )}
          {items.map((a) => (
            <div
              key={a.id}
              className={`rounded-2xl border p-4 transition-opacity
                ${NIVEL_STYLE[a.nivel] || 'border-slate-200 bg-slate-50 text-slate-700'}
                ${a.leida ? 'opacity-50' : ''}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-2 min-w-0">
                  <span className="text-lg shrink-0 mt-0.5">{NIVEL_ICON[a.nivel] || '📋'}</span>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-bold uppercase tracking-wide">{a.nivel}</span>
                      {a.leida && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-white/60 font-medium">
                          {t('alerta.leida_badge')}
                        </span>
                      )}
                    </div>
                    <p className="text-sm mt-0.5 font-medium">{a.mensaje}</p>
                    <p className="text-xs mt-1 opacity-70">
                      {new Date(a.timestamp).toLocaleString()} · {t('common.value')}: {a.valorRegistrado}
                    </p>
                    {a.sensor && (
                      <p className="text-xs opacity-60 mt-0.5">
                        {t('alerta.sensor')}: {a.sensor.codigo || a.sensor.id}
                      </p>
                    )}
                  </div>
                </div>
                {!a.leida && (
                  <ActionBtn onClick={() => handleMarcarLeida(a.id)} variant="secondary">
                    {t('alerta.marcarLeida')}
                  </ActionBtn>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
