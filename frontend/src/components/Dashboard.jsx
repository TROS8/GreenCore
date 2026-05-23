/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista principal del dashboard con estadisticas del invernadero.
 *
 * @module components/Dashboard
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { getAllSensors } from '../services/sensorService'
import { getAllZonas } from '../services/zonaService'
import { getAllPlantas } from '../services/plantaService'
import { getAlertasNoLeidas } from '../services/alertaService'

function KpiCard({ label, value, color, icon }) {
  return (
    <div className={`bg-white rounded-lg p-5 shadow-sm border-l-4 ${color}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">{label}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [sensors, setSensors] = useState([])
  const [zonas, setZonas] = useState([])
  const [plantas, setPlantas] = useState([])
  const [alertas, setAlertas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAllSensors(), getAllZonas(), getAllPlantas(), getAlertasNoLeidas()])
      .then(([s, z, p, a]) => {
        setSensors(s)
        setZonas(z)
        setPlantas(p)
        setAlertas(a)
      })
      .finally(() => setLoading(false))
  }, [])

  const sensoresActivos = sensors.filter((s) => s.estado === 'ACTIVO').length
  const zonasActivas = zonas.filter((z) => z.activa).length
  const plantasVenta = plantas.filter((p) => p.estado === 'LISTA_VENTA').length
  const alertasNoLeidas = alertas.length

  const chartData = sensors.map((s) => ({
    name: s.codigo,
    valor: s.valorActual ?? 0,
    min: s.umbralMinimo,
    max: s.umbralMaximo,
  }))

  if (loading) return <p className="text-slate-500 p-4">Cargando dashboard...</p>

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Zonas activas" value={zonasActivas} color="border-emerald-500" icon="🌿" />
        <KpiCard label="Sensores activos" value={sensoresActivos} color="border-blue-500" icon="📡" />
        <KpiCard label="Plantas listas p/ venta" value={plantasVenta} color="border-teal-500" icon="🌱" />
        <KpiCard
          label="Alertas sin leer"
          value={alertasNoLeidas}
          color={alertasNoLeidas > 0 ? 'border-red-500' : 'border-slate-300'}
          icon={alertasNoLeidas > 0 ? '🚨' : '✅'}
        />
      </div>

      <div className="bg-white rounded-lg p-5 shadow-sm">
        <h3 className="text-base font-semibold mb-4 text-slate-700">Valores actuales de sensores</h3>
        {chartData.length === 0 ? (
          <p className="text-slate-400 text-sm">Sin datos de sensores.</p>
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="valor" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} name="Valor" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {sensors.map((s) => {
          const pct = s.umbralMaximo > s.umbralMinimo
            ? Math.min(100, Math.max(0, ((s.valorActual ?? 0) - s.umbralMinimo) / (s.umbralMaximo - s.umbralMinimo) * 100))
            : 0
          const outOfRange = s.valorActual != null && (s.valorActual < s.umbralMinimo || s.valorActual > s.umbralMaximo)
          return (
            <div key={s.id} className={`bg-white rounded-lg p-4 shadow-sm border ${outOfRange ? 'border-red-300' : 'border-slate-200'}`}>
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-sm">{s.codigo}</p>
                  <p className="text-xs text-slate-400">{s.tipo} · {s.zona?.nombre || '—'}</p>
                </div>
                {outOfRange && <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Fuera de rango</span>}
              </div>
              <p className="text-2xl font-bold mt-2">
                {s.valorActual ?? '—'} <span className="text-sm font-normal text-slate-500">{s.unidad}</span>
              </p>
              <div className="mt-2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${outOfRange ? 'bg-red-400' : 'bg-emerald-400'}`} style={{ width: `${pct}%` }} />
              </div>
              <p className="text-xs text-slate-400 mt-1">{s.umbralMinimo} – {s.umbralMaximo} {s.unidad}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
