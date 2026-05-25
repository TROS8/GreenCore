/**
 * GreenCore — Vista CRUD de plantas cultivadas.
 *
 * @module components/PlantaList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllPlantas, createPlanta, updatePlanta, deletePlanta } from '../services/plantaService'
import { getAllZonas } from '../services/zonaService'
import { Modal } from './Modal'
import {
  inp, Spinner, EmptyState, PageHeader,
  Field, FormActions, ErrorBanner, ActionBtn,
} from './ui'

const ESTADO_COLOR = {
  SEMILLA:     'bg-amber-100  text-amber-700',
  GERMINANDO:  'bg-lime-100   text-lime-700',
  CRECIMIENTO: 'bg-green-100  text-green-700',
  LISTA_VENTA: 'bg-teal-100   text-teal-700',
  VENDIDA:     'bg-slate-100  text-slate-500',
  BAJA:        'bg-red-100    text-red-500',
}

const ESTADOS = ['SEMILLA', 'GERMINANDO', 'CRECIMIENTO', 'LISTA_VENTA', 'VENDIDA', 'BAJA']

const EMPTY = {
  nombre: '', especie: '', lote: '', cantidad: 1, precio: 0,
  estado: 'SEMILLA', fechaSiembra: '', fechaEstimadaVenta: '',
  descripcion: '', zonaId: '',
}

export function PlantaList() {
  const { t } = useTranslation()
  const [items,   setItems]   = useState([])
  const [zonas,   setZonas]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState(null)
  const [form,    setForm]    = useState(EMPTY)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState(null)

  const reload = () => {
    Promise.all([getAllPlantas(), getAllZonas()])
      .then(([p, z]) => { setItems(p); setZonas(z) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit   = (p) => {
    setForm({ ...p, zonaId: p.zona?.id || '' }); setError(null); setModal('edit')
  }
  const closeModal = () => { setModal(null); setError(null) }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const handleSave = async () => {
    setSaving(true); setError(null)
    try {
      const payload = { ...form, zona: form.zonaId ? { id: parseInt(form.zonaId) } : null }
      if (modal === 'edit') await updatePlanta(form.id, payload)
      else                  await createPlanta(payload)
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(t('planta.confirmDelete'))) return
    await deletePlanta(id); reload()
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('planta.title')}
        count={items.length}
        onNew={openCreate}
        btnLabel={t('planta.new')}
      />

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="🌱" message={t('planta.noData')} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((p) => (
            <div key={p.id}
              className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow">
              {p.imagenUrl && (
                <img src={p.imagenUrl} alt={p.nombre} className="w-full h-36 object-cover" />
              )}
              <div className="p-5 flex flex-col gap-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-slate-800">{p.nombre}</h3>
                    {p.especie && <p className="text-xs italic text-slate-400">{p.especie}</p>}
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_COLOR[p.estado] || 'bg-slate-100 text-slate-600'}`}>
                    {p.estado}
                  </span>
                </div>

                <div className="text-xs text-slate-500 space-y-1">
                  <p>{t('planta.lote')}: <span className="font-mono font-medium text-slate-700">{p.lote}</span></p>
                  <p>{t('planta.cantidad')}: {p.cantidad} · ${Number(p.precio).toLocaleString()}</p>
                  {p.fechaSiembra && <p>{t('planta.fechaSiembra')}: {p.fechaSiembra}</p>}
                  {p.zona && <p>{t('planta.zona')}: {p.zona.nombre || p.zona}</p>}
                </div>

                <div className="flex gap-2 pt-1">
                  <ActionBtn onClick={() => openEdit(p)}>{t('common.edit')}</ActionBtn>
                  <ActionBtn onClick={() => handleDelete(p.id)} variant="danger">{t('common.delete')}</ActionBtn>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {modal && (
        <Modal
          title={modal === 'edit' ? t('planta.edit') : t('planta.new')}
          onClose={closeModal}
        >
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('planta.nombre')} required>
                <input name="nombre" value={form.nombre} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('planta.especie')}>
                <input name="especie" value={form.especie || ''} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('planta.lote')} required>
                <input name="lote" value={form.lote} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('planta.estado')}>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('planta.cantidad')}>
                <input type="number" name="cantidad" value={form.cantidad} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('planta.precio')}>
                <input type="number" name="precio" value={form.precio} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('planta.fechaSiembra')}>
                <input type="date" name="fechaSiembra" value={form.fechaSiembra || ''} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('planta.fechaEstimadaVenta')}>
                <input type="date" name="fechaEstimadaVenta" value={form.fechaEstimadaVenta || ''} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <Field label={t('planta.zona')}>
              <select name="zonaId" value={form.zonaId} onChange={handleChange} className={inp}>
                <option value="">{t('common.selectZone')}</option>
                {zonas.map((z) => <option key={z.id} value={z.id}>{z.nombre}</option>)}
              </select>
            </Field>
            <Field label={t('planta.descripcion')}>
              <textarea name="descripcion" value={form.descripcion || ''} onChange={handleChange} rows={2} className={inp} />
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
