/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista principal del dashboard con estadisticas del invernadero.
 * Rediseniado con cards modernas, gradientes y mejor organizacion visual.
 *
 * @module components/Dashboard
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts'
import { getAllSensors }      from '../services/sensorService'
import { getAllZonas }         from '../services/zonaService'
import { getAllPlantas }       from '../services/plantaService'
import { getAlertasNoLeidas } from '../services/alertaService'
import { useStore }            from '../store/useStore'

// ── KPI Card ─────────────────────────────────────────────────────────────────

function KpiCard({ label, value, gradient, icon, sub }) {
  return (
    <div className={`relative overflow-hidden rounded-2xl p-5 text-white shadow-md ${gradient}`}>
      <div className="absolute -right-3 -top-3 text-6xl opacity-20 select-none">{icon}</div>
      <p className="text-xs font-semibold uppercase tracking-widest opacity-80">{label}</p>
      <p className="text-4xl font-extrabold mt-1 leading-none">{value}</p>
      {sub && <p className="text-xs mt-2 opacity-70">{sub}</p>}
    </div>
  )
}

// ── Sensor Card ───────────────────────────────────────────────────────────────

function SensorCard({ sensor }) {
  const pct = sensor.umbralMaximo > sensor.umbralMinimo
    ? Math.min(100, Math.max(0,
        ((sensor.valorActual ?? 0) - sensor.umbralMinimo) /
        (sensor.umbralMaximo - sensor.umbralMinimo) * 100))
    : 0
  const outOfRange = sensor.valorActual != null &&
    (sensor.valorActual < sensor.umbralMinimo || sensor.valorActual > sensor.umbralMaximo)
  const TIPO_ICON = { TEMPERATURA:'🌡️', HUMEDAD:'💧', LUZ:'☀️', CO2:'🌫️', PH:'⚗️' }

  return (
    <div className={`bg-white rounded-2xl p-4 shadow-sm border transition-all
                     ${outOfRange ? 'border-red-300 shadow-red-100' : 'border-slate-100 hover:shadow-md'}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-1.5">
            <span className="text-lg">{TIPO_ICON[sensor.tipo] || '📡'}</span>
            <p className="font-bold text-slate-800 text-sm">{sensor.codigo}</p>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">{sensor.zona?.nombre || '—'}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          {outOfRange && (
            <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold">
              Fuera de rango
            </span>
          )}
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium
            ${sensor.estado === 'ACTIVO'
              ? 'bg-green-100 text-green-700'
              : sensor.estado === 'INACTIVO'
              ? 'bg-slate-100 text-slate-500'
              : 'bg-red-100 text-red-600'}`}>
            {sensor.estado}
          </span>
        </div>
      </div>

      <p className="text-3xl font-extrabold text-slate-800">
        {sensor.valorActual ?? '—'}
        <span className="text-sm font-normal text-slate-400 ml-1">{sensor.unidad}</span>
      </p>

      {/* Barra de progreso */}
      <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700
            ${outOfRange ? 'bg-red-400' : pct > 75 ? 'bg-amber-400' : 'bg-emerald-400'}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-slate-400 mt-1">
        <span>{sensor.umbralMinimo}</span>
        <span>{sensor.umbralMaximo} {sensor.unidad}</span>
      </div>
    </div>
  )
}

// ── Tooltip personalizado ─────────────────────────────────────────────────────

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-lg px-3 py-2 text-xs">
      <p className="font-bold text-slate-700 mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <strong>{p.value}</strong>
        </p>
      ))}
    </div>
  )
}

// ── Dashboard principal ───────────────────────────────────────────────────────

export default function Dashboard() {
  const user    = useStore((s) => s.user)
  const role    = useStore((s) => s.role)
  const [sensors,  setSensors]  = useState([])
  const [zonas,    setZonas]    = useState([])
  const [plantas,  setPlantas]  = useState([])
  const [alertas,  setAlertas]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([getAllSensors(), getAllZonas(), getAllPlantas(), getAlertasNoLeidas()])
      .then(([s, z, p, a]) => {
        setSensors(s); setZonas(z); setPlantas(p); setAlertas(a)
      })
      .finally(() => setLoading(false))
  }, [])

  const sensoresActivos = sensors.filter((s) => s.estado === 'ACTIVO').length
  const zonasActivas    = zonas.filter((z) => z.activa).length
  const plantasVenta    = plantas.filter((p) => p.estado === 'LISTA_VENTA').length
  const alertasNoLeidas = alertas.length

  const chartData = sensors
    .filter((s) => s.valorActual != null)
    .map((s) => ({
      name:  s.codigo,
      valor: s.valorActual,
      max:   s.umbralMaximo,
      min:   s.umbralMinimo,
    }))

  const hora = new Date().getHours()
  const saludo = hora < 12 ? 'Buenos días' : hora < 18 ? 'Buenas tardes' : 'Buenas noches'

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4 text-slate-400">
        <svg className="animate-spin h-10 w-10 text-emerald-500" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
        </svg>
        <p className="text-sm">Cargando invernadero...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">

      {/* Bienvenida */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-800">
            {saludo}{user?.nombre ? `, ${user.nombre.split(' ')[0]}` : ''} 👋
          </h1>
          <p className="text-slate-500 text-sm mt-0.5">
            Resumen del invernadero · {new Date().toLocaleDateString('es-CO', { weekday:'long', day:'numeric', month:'long' })}
          </p>
        </div>
        {role && (
          <span className={`text-xs px-3 py-1 rounded-full font-bold shadow-sm
            ${role === 'ADMIN' ? 'bg-red-100 text-red-700'
              : role === 'OPERARIO' ? 'bg-blue-100 text-blue-700'
              : 'bg-slate-100 text-slate-600'}`}>
            {role}
          </span>
        )}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Zonas activas"
          value={zonasActivas}
          gradient="bg-gradient-to-br from-emerald-500 to-teal-600"
          icon="🌿"
          sub={`de ${zonas.length} totales`}
        />
        <KpiCard
          label="Sensores activos"
          value={sensoresActivos}
          gradient="bg-gradient-to-br from-blue-500 to-indigo-600"
          icon="📡"
          sub={`de ${sensors.length} totales`}
        />
        <KpiCard
          label="Listas p/ venta"
          value={plantasVenta}
          gradient="bg-gradient-to-br from-teal-500 to-cyan-600"
          icon="🌱"
          sub={`de ${plantas.length} plantas`}
        />
        <KpiCard
          label="Alertas sin leer"
          value={alertasNoLeidas}
          gradient={alertasNoLeidas > 0
            ? "bg-gradient-to-br from-red-500 to-rose-600"
            : "bg-gradient-to-br from-slate-400 to-slate-500"}
          icon={alertasNoLeidas > 0 ? '🚨' : '✅'}
          sub={alertasNoLeidas > 0 ? 'Revisión requerida' : 'Todo en orden'}
        />
      </div>

      {/* Gráfico de sensores */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
          <h3 className="text-base font-bold text-slate-700 mb-4">
            Valores actuales de sensores
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorValor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#10b981" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone" dataKey="valor" stroke="#10b981" strokeWidth={2.5}
                  fill="url(#colorValor)" dot={{ r: 4, fill: '#10b981', strokeWidth: 0 }}
                  name="Valor"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Cards de sensores */}
      {sensors.length > 0 && (
        <div>
          <h3 className="text-base font-bold text-slate-700 mb-3">Estado de sensores</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {sensors.map((s) => <SensorCard key={s.id} sensor={s} />)}
          </div>
        </div>
      )}

      {/* Estado vacío */}
      {sensors.length === 0 && zonas.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-3">
          <span className="text-6xl">🌿</span>
          <p className="text-lg font-semibold">El invernadero está vacío</p>
          <p className="text-sm">Comienza creando zonas y sensores desde el menú lateral.</p>
        </div>
      )}
    </div>
  )
}
