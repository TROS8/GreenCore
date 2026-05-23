/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista CRUD de sensores fisicos. Muestra tipo, estado y ultima lectura.
 *
 * @module components/SensorList
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { getAllSensors, createSensor, updateSensor, deleteSensor, registrarLectura } from '../services/sensorService'
import { getAllZonas } from '../services/zonaService'
import { Modal } from './Modal'

const estadoColor = {
  ACTIVO: 'bg-green-100 text-green-700',
  INACTIVO: 'bg-slate-200 text-slate-500',
  FALLA: 'bg-red-100 text-red-700',
  CALIBRANDO: 'bg-yellow-100 text-yellow-700',
}

const TIPOS = ['TEMPERATURA', 'HUMEDAD', 'LUMINOSIDAD', 'CO2', 'PH_SUELO']
const ESTADOS_SENSOR = ['ACTIVO', 'INACTIVO', 'FALLA', 'CALIBRANDO']
const inp = 'mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500'

const EMPTY = {
  codigo: '', tipo: 'TEMPERATURA', valorActual: null, unidad: '°C',
  umbralMinimo: 0, umbralMaximo: 100, estado: 'ACTIVO', zonaId: '',
}

export function SensorList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [zonas, setZonas] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)  // null | 'create' | 'edit' | 'lectura'
  const [form, setForm] = useState(EMPTY)
  const [lecturaValor, setLecturaValor] = useState('')
  const [activeSensorId, setActiveSensorId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = () => {
    Promise.all([getAllSensors(), getAllZonas()])
      .then(([s, z]) => { setItems(s); setZonas(z) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit = (s) => { setForm({ ...s, zonaId: s.zona?.id || '' }); setError(null); setModal('edit') }
  const openLectura = (id) => { setActiveSensorId(id); setLecturaValor(''); setError(null); setModal('lectura') }
  const closeModal = () => { setModal(null); setActiveSensorId(null); setError(null) }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const buildPayload = () => ({
    ...form,
    zona: form.zonaId ? { id: parseInt(form.zonaId) } : null,
  })

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const payload = buildPayload()
      if (modal === 'edit') await updateSensor(form.id, payload)
      else await createSensor(payload)
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar. Verifica los datos e intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  const handleLectura = async () => {
    const val = parseFloat(lecturaValor)
    if (isNaN(val)) return
    setSaving(true)
    setError(null)
    try {
      await registrarLectura(activeSensorId, val)
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al registrar la lectura.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este sensor?')) return
    await deleteSensor(id)
    reload()
  }

  const chartData = items.map((s) => ({ name: s.codigo, value: s.valorActual ?? 0 }))

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">{t('sensor.title')}</h2>
        <button onClick={openCreate} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
          + {t('common.create')}
        </button>
      </div>

      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map((s) => (
              <div key={s.id} className="border rounded-lg p-4 bg-slate-50">
                <div className="flex justify-between items-start">
                  <h3 className="font-semibold">{s.codigo}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${estadoColor[s.estado] || 'bg-slate-100'}`}>
                    {s.estado}
                  </span>
                </div>
                <p className="text-sm text-slate-500">{s.tipo} · {s.zona?.nombre || '—'}</p>
                <div className="text-2xl font-bold mt-2">
                  {s.valorActual ?? '—'} <span className="text-sm font-normal text-slate-500">{s.unidad}</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">Rango: {s.umbralMinimo} – {s.umbralMaximo}</p>
                <div className="mt-3 flex gap-2 flex-wrap">
                  <button onClick={() => openLectura(s.id)} className="text-xs px-3 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700">
                    + Lectura
                  </button>
                  <button onClick={() => openEdit(s)} className="text-xs px-3 py-1 rounded border border-slate-300 hover:bg-slate-100">{t('common.edit')}</button>
                  <button onClick={() => handleDelete(s.id)} className="text-xs px-3 py-1 rounded border border-red-200 text-red-600 hover:bg-red-50">{t('common.delete')}</button>
                </div>
              </div>
            ))}
          </div>

          {chartData.length > 0 && (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {modal === 'lectura' && (
        <Modal title="Registrar Lectura" onClose={closeModal}>
          <div className="space-y-4">
            <p className="text-sm text-slate-600">Ingresa el nuevo valor del sensor. Si está fuera del rango configurado, se generará una alerta automáticamente.</p>
            <div>
              <label className="text-sm font-medium text-slate-700">Valor *</label>
              <input
                type="number"
                step="0.1"
                value={lecturaValor}
                onChange={(e) => setLecturaValor(e.target.value)}
                className={inp}
                placeholder="Ej: 25.3"
                autoFocus
              />
            </div>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{error}</p>}
            <div className="flex justify-end gap-2">
              <button onClick={closeModal} className="px-4 py-2 text-sm rounded-lg border border-slate-300 hover:bg-slate-50">{t('common.cancel')}</button>
              <button onClick={handleLectura} disabled={saving || !lecturaValor} className="px-4 py-2 text-sm rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50">
                {saving ? '...' : 'Registrar'}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {(modal === 'create' || modal === 'edit') && (
        <Modal title={modal === 'edit' ? 'Editar Sensor' : 'Nuevo Sensor'} onClose={closeModal}>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.codigo')} *</label>
                <input name="codigo" value={form.codigo} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.tipo')}</label>
                <select name="tipo" value={form.tipo} onChange={handleChange} className={inp}>
                  {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.unidad')}</label>
                <input name="unidad" value={form.unidad} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.estado')}</label>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS_SENSOR.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.umbralMinimo')}</label>
                <input type="number" name="umbralMinimo" value={form.umbralMinimo} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('sensor.umbralMaximo')}</label>
                <input type="number" name="umbralMaximo" value={form.umbralMaximo} onChange={handleChange} className={inp} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('sensor.zona')}</label>
              <select name="zonaId" value={form.zonaId} onChange={handleChange} className={inp}>
                <option value="">— Seleccionar zona —</option>
                {zonas.map((z) => <option key={z.id} value={z.id}>{z.nombre}</option>)}
              </select>
            </div>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{error}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={closeModal} className="px-4 py-2 text-sm rounded-lg border border-slate-300 hover:bg-slate-50">{t('common.cancel')}</button>
              <button onClick={handleSave} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50">
                {saving ? '...' : t('common.save')}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
