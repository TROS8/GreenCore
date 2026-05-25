/**
 * GreenCore — Vista CRUD de zonas fisicas del invernadero.
 *
 * @module components/ZonaList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllZonas, createZona, updateZona, deleteZona } from '../services/zonaService'
import { Modal } from './Modal'
import {
  inp, Spinner, EmptyState, PageHeader,
  Field, FormActions, ErrorBanner, StatusBadge, ActionBtn,
} from './ui'

const EMPTY = {
  nombre: '', descripcion: '', capacidadMaxima: 100,
  temperaturaMinima: 15, temperaturaMaxima: 30,
  humedadMinima: 40, humedadMaxima: 80, activa: true,
}

export function ZonaList() {
  const { t } = useTranslation()
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState(null)
  const [form,    setForm]    = useState(EMPTY)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState(null)

  const reload = () => getAllZonas().then(setItems).finally(() => setLoading(false))
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY);    setError(null); setModal('create') }
  const openEdit   = (z) => { setForm({ ...z }); setError(null); setModal('edit')   }
  const closeModal = ()  => { setModal(null);   setError(null) }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSave = async () => {
    setSaving(true); setError(null)
    try {
      if (modal === 'edit') await updateZona(form.id, form)
      else                  await createZona(form)
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(t('zona.confirmDelete'))) return
    await deleteZona(id); reload()
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('zona.title')}
        count={items.length}
        onNew={openCreate}
        btnLabel={t('zona.new')}
      />

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="🌿" message={t('zona.noData')} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((z) => (
            <div key={z.id}
              className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-slate-800">{z.nombre}</h3>
                  {z.descripcion && (
                    <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{z.descripcion}</p>
                  )}
                </div>
                <StatusBadge active={z.activa} />
              </div>

              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  🌡️ {z.temperaturaMinima}° – {z.temperaturaMaxima}°C
                </span>
                <span className="flex items-center gap-1">
                  💧 {z.humedadMinima}% – {z.humedadMaxima}%
                </span>
                <span className="flex items-center gap-1">
                  📦 {t('zona.capacidadMaxima')}: {z.capacidadMaxima}
                </span>
              </div>

              <div className="flex gap-2 pt-1">
                <ActionBtn onClick={() => openEdit(z)}>{t('common.edit')}</ActionBtn>
                <ActionBtn onClick={() => handleDelete(z.id)} variant="danger">{t('common.delete')}</ActionBtn>
              </div>
            </div>
          ))}
        </div>
      )}

      {modal && (
        <Modal
          title={modal === 'edit' ? t('zona.edit') : t('zona.new')}
          onClose={closeModal}
        >
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
                <label className="flex items-center gap-2 mt-2 cursor-pointer select-none">
                  <input type="checkbox" name="activa" checked={form.activa} onChange={handleChange}
                    className="w-4 h-4 accent-emerald-600" />
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
            <ErrorBanner message={error} />
            <FormActions onCancel={closeModal} onSave={handleSave} saving={saving}
              saveLabel={t('common.save')} cancelLabel={t('common.cancel')} />
          </div>
        </Modal>
      )}
    </div>
  )
}
