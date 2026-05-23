import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllZonas, createZona, updateZona, deleteZona } from '../services/zonaService'
import { Modal } from './Modal'

const EMPTY = {
  nombre: '', descripcion: '', capacidadMaxima: 100,
  temperaturaMinima: 15, temperaturaMaxima: 30,
  humedadMinima: 40, humedadMaxima: 80, activa: true,
}

export function ZonaList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = () => getAllZonas().then(setItems).finally(() => setLoading(false))
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit = (z) => { setForm({ ...z }); setError(null); setModal('edit') }
  const closeModal = () => { setModal(null); setError(null) }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      if (modal === 'edit') await updateZona(form.id, form)
      else await createZona(form)
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar. Verifica los datos e intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta zona?')) return
    await deleteZona(id)
    reload()
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{t('zona.title')}</h2>
        <button onClick={openCreate} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
          + {t('common.create')}
        </button>
      </div>

      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((z) => (
            <div key={z.id} className="border rounded-lg p-4 bg-slate-50">
              <div className="flex justify-between items-start">
                <h3 className="font-semibold text-lg">{z.nombre}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${z.activa ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-500'}`}>
                  {z.activa ? t('common.active') : t('common.inactive')}
                </span>
              </div>
              <p className="text-sm text-slate-500 mt-1">{z.descripcion}</p>
              <div className="mt-3 grid grid-cols-2 gap-1 text-xs text-slate-600">
                <span>🌡 {z.temperaturaMinima}°–{z.temperaturaMaxima}°C</span>
                <span>💧 {z.humedadMinima}%–{z.humedadMaxima}%</span>
                <span>📦 Cap. {z.capacidadMaxima}</span>
              </div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => openEdit(z)} className="text-xs px-3 py-1 rounded border border-slate-300 hover:bg-slate-100">
                  {t('common.edit')}
                </button>
                <button onClick={() => handleDelete(z.id)} className="text-xs px-3 py-1 rounded border border-red-200 text-red-600 hover:bg-red-50">
                  {t('common.delete')}
                </button>
              </div>
            </div>
          ))}
          {items.length === 0 && <p className="text-slate-400 text-sm col-span-3">Sin zonas registradas.</p>}
        </div>
      )}

      {modal && (
        <Modal title={modal === 'edit' ? 'Editar Zona' : 'Nueva Zona'} onClose={closeModal}>
          <div className="space-y-3">
            <Field label={t('zona.nombre')} required>
              <input name="nombre" value={form.nombre} onChange={handleChange} className={inp} />
            </Field>
            <Field label={t('zona.descripcion')}>
              <textarea name="descripcion" value={form.descripcion || ''} onChange={handleChange} rows={2} className={inp} />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('zona.capacidadMaxima')}>
                <input type="number" name="capacidadMaxima" value={form.capacidadMaxima} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('zona.activa')}>
                <label className="flex items-center gap-2 mt-2 cursor-pointer">
                  <input type="checkbox" name="activa" checked={form.activa} onChange={handleChange} className="w-4 h-4 accent-emerald-600" />
                  <span className="text-sm">{form.activa ? t('common.active') : t('common.inactive')}</span>
                </label>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('zona.temperaturaMinima')}>
                <input type="number" name="temperaturaMinima" value={form.temperaturaMinima} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('zona.temperaturaMaxima')}>
                <input type="number" name="temperaturaMaxima" value={form.temperaturaMaxima} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('zona.humedadMinima')}>
                <input type="number" name="humedadMinima" value={form.humedadMinima} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('zona.humedadMaxima')}>
                <input type="number" name="humedadMaxima" value={form.humedadMaxima} onChange={handleChange} className={inp} />
              </Field>
            </div>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">{error}</p>}
            <FormActions onCancel={closeModal} onSave={handleSave} saving={saving} t={t} />
          </div>
        </Modal>
      )}
    </div>
  )
}

const inp = 'mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500'

function Field({ label, required, children }) {
  return (
    <div>
      <label className="text-sm font-medium text-slate-700">{label}{required && ' *'}</label>
      {children}
    </div>
  )
}

function FormActions({ onCancel, onSave, saving, t }) {
  return (
    <div className="flex justify-end gap-2 pt-2">
      <button onClick={onCancel} className="px-4 py-2 text-sm rounded-lg border border-slate-300 hover:bg-slate-50">
        {t('common.cancel')}
      </button>
      <button onClick={onSave} disabled={saving} className="px-4 py-2 text-sm rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50">
        {saving ? '...' : t('common.save')}
      </button>
    </div>
  )
}
