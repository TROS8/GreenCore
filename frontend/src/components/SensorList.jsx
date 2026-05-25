/**
 * GreenCore — Vista CRUD de sensores fisicos.
 *
 * @module components/SensorList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllSensors, createSensor, updateSensor, deleteSensor, registrarLectura } from '../services/sensorService'
import { getAllZonas } from '../services/zonaService'
import { Modal } from './Modal'
import {
  inp, Spinner, EmptyState, PageHeader,
  Field, FormActions, ErrorBanner, ActionBtn,
} from './ui'

const ESTADO_COLOR = {
  ACTIVO:     'bg-green-100  text-green-700',
  INACTIVO:   'bg-slate-100  text-slate-500',
  FALLA:      'bg-red-100    text-red-700',
  CALIBRANDO: 'bg-yellow-100 text-yellow-700',
}

const TIPO_ICON = { TEMPERATURA:'🌡️', HUMEDAD:'💧', LUMINOSIDAD:'☀️', CO2:'🌫️', PH_SUELO:'⚗️' }
const TIPOS          = ['TEMPERATURA', 'HUMEDAD', 'LUMINOSIDAD', 'CO2', 'PH_SUELO']
const ESTADOS_SENSOR = ['ACTIVO', 'INACTIVO', 'FALLA', 'CALIBRANDO']

const EMPTY = {
  codigo: '', tipo: 'TEMPERATURA', valorActual: null, unidad: '°C',
  umbralMinimo: 0, umbralMaximo: 100, estado: 'ACTIVO', zonaId: '',
}

export function SensorList() {
  const { t } = useTranslation()
  const [items,          setItems]          = useState([])
  const [zonas,          setZonas]          = useState([])
  const [loading,        setLoading]        = useState(true)
  const [modal,          setModal]          = useState(null)
  const [form,           setForm]           = useState(EMPTY)
  const [lecturaValor,   setLecturaValor]   = useState('')
  const [activeSensorId, setActiveSensorId] = useState(null)
  const [saving,         setSaving]         = useState(false)
  const [error,          setError]          = useState(null)

  const reload = () => {
    Promise.all([getAllSensors(), getAllZonas()])
      .then(([s, z]) => { setItems(s); setZonas(z) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [])

  const openCreate  = ()  => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit    = (s) => { setForm({ ...s, zonaId: s.zona?.id || '' }); setError(null); setModal('edit') }
  const openLectura = (id) => { setActiveSensorId(id); setLecturaValor(''); setError(null); setModal('lectura') }
  const closeModal  = ()  => { setModal(null); setActiveSensorId(null); setError(null) }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const handleSave = async () => {
    setSaving(true); setError(null)
    try {
      const payload = { ...form, zona: form.zonaId ? { id: parseInt(form.zonaId) } : null }
      if (modal === 'edit') await updateSensor(form.id, payload)
      else                  await createSensor(payload)
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const handleLectura = async () => {
    const val = parseFloat(lecturaValor)
    if (isNaN(val)) return
    setSaving(true); setError(null)
    try {
      await registrarLectura(activeSensorId, val)
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al registrar.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(t('sensor.confirmDelete'))) return
    await deleteSensor(id); reload()
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('sensor.title')}
        count={items.length}
        onNew={openCreate}
        btnLabel={t('sensor.new')}
      />

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="📡" message={t('sensor.noData')} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((s) => {
            const pct = s.umbralMaximo > s.umbralMinimo
              ? Math.min(100, Math.max(0,
                  ((s.valorActual ?? 0) - s.umbralMinimo) /
                  (s.umbralMaximo - s.umbralMinimo) * 100))
              : 0
            const outOfRange = s.valorActual != null &&
              (s.valorActual < s.umbralMinimo || s.valorActual > s.umbralMaximo)

            return (
              <div key={s.id}
                className={`bg-white rounded-2xl p-5 shadow-sm border transition-all hover:shadow-md
                  ${outOfRange ? 'border-red-300' : 'border-slate-100'}`}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-base">{TIPO_ICON[s.tipo] || '📡'}</span>
                      <p className="font-bold text-slate-800 text-sm">{s.codigo}</p>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{s.tipo} · {s.zona?.nombre || '—'}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    {outOfRange && (
                      <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-semibold">
                        {t('lectura.fueraDeRango')}
                      </span>
                    )}
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_COLOR[s.estado] || 'bg-slate-100'}`}>
                      {s.estado}
                    </span>
                  </div>
                </div>

                <p className="text-3xl font-extrabold text-slate-800">
                  {s.valorActual ?? '—'}
                  <span className="text-sm font-normal text-slate-400 ml-1">{s.unidad}</span>
                </p>

                <div className="mt-3 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700
                      ${outOfRange ? 'bg-red-400' : pct > 75 ? 'bg-amber-400' : 'bg-emerald-400'}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  {t('common.range')}: {s.umbralMinimo} – {s.umbralMaximo} {s.unidad}
                </p>

                <div className="flex gap-2 flex-wrap mt-3">
                  <ActionBtn onClick={() => openLectura(s.id)} variant="primary">
                    {t('sensor.addLectura')}
                  </ActionBtn>
                  <ActionBtn onClick={() => openEdit(s)}>{t('common.edit')}</ActionBtn>
                  <ActionBtn onClick={() => handleDelete(s.id)} variant="danger">{t('common.delete')}</ActionBtn>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Modal registrar lectura */}
      {modal === 'lectura' && (
        <Modal title={t('sensor.registrarLectura')} onClose={closeModal}>
          <div className="space-y-4">
            <p className="text-sm text-slate-500">{t('sensor.lecturaInfo')}</p>
            <Field label={t('common.value')} required>
              <input
                type="number" step="0.1"
                value={lecturaValor}
                onChange={(e) => setLecturaValor(e.target.value)}
                className={inp}
                placeholder="Ej: 25.3"
                autoFocus
              />
            </Field>
            <ErrorBanner message={error} />
            <FormActions
              onCancel={closeModal}
              onSave={handleLectura}
              saving={saving}
              saveLabel={t('common.register')}
              cancelLabel={t('common.cancel')}
            />
          </div>
        </Modal>
      )}

      {/* Modal crear / editar sensor */}
      {(modal === 'create' || modal === 'edit') && (
        <Modal
          title={modal === 'edit' ? t('sensor.edit') : t('sensor.new')}
          onClose={closeModal}
        >
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('sensor.codigo')} required>
                <input name="codigo" value={form.codigo} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('sensor.tipo')}>
                <select name="tipo" value={form.tipo} onChange={handleChange} className={inp}>
                  {TIPOS.map((tp) => <option key={tp} value={tp}>{tp}</option>)}
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('sensor.unidad')}>
                <input name="unidad" value={form.unidad} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('sensor.estado')}>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS_SENSOR.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('sensor.umbralMinimo')}>
                <input type="number" name="umbralMinimo" value={form.umbralMinimo} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('sensor.umbralMaximo')}>
                <input type="number" name="umbralMaximo" value={form.umbralMaximo} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <Field label={t('sensor.zona')}>
              <select name="zonaId" value={form.zonaId} onChange={handleChange} className={inp}>
                <option value="">{t('common.selectZone')}</option>
                {zonas.map((z) => <option key={z.id} value={z.id}>{z.nombre}</option>)}
              </select>
            </Field>
            <ErrorBanner message={error} />
            <FormActions onCancel={closeModal} onSave={handleSave} saving={saving}
              saveLabel={t('common.save')} cancelLabel={t('common.cancel')} />
          </div>
        </Modal>
      )}
    </div>
  )
}
