import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllPlantas, createPlanta, updatePlanta, deletePlanta } from '../services/plantaService'
import { getAllZonas } from '../services/zonaService'
import { Modal } from './Modal'

const estadoColor = {
  SEMILLA: 'bg-amber-100 text-amber-700',
  GERMINANDO: 'bg-lime-100 text-lime-700',
  CRECIMIENTO: 'bg-green-100 text-green-700',
  LISTA_VENTA: 'bg-teal-100 text-teal-700',
  VENDIDA: 'bg-slate-200 text-slate-500',
  BAJA: 'bg-red-100 text-red-500',
}

const ESTADOS = ['SEMILLA', 'GERMINANDO', 'CRECIMIENTO', 'LISTA_VENTA', 'VENDIDA', 'BAJA']
const inp = 'mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500'

const EMPTY = {
  nombre: '', especie: '', lote: '', cantidad: 1, precio: 0,
  estado: 'SEMILLA', fechaSiembra: '', fechaEstimadaVenta: '',
  descripcion: '', zonaId: '',
}

export function PlantaList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [zonas, setZonas] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = () => {
    Promise.all([getAllPlantas(), getAllZonas()])
      .then(([p, z]) => { setItems(p); setZonas(z) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit = (p) => {
    setForm({ ...p, zonaId: p.zona?.id || '' })
    setError(null)
    setModal('edit')
  }
  const closeModal = () => { setModal(null); setError(null) }

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
      if (modal === 'edit') await updatePlanta(form.id, payload)
      else await createPlanta(payload)
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar. Verifica los datos e intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta planta?')) return
    await deletePlanta(id)
    reload()
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{t('planta.title')}</h2>
        <button onClick={openCreate} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
          + {t('common.create')}
        </button>
      </div>

      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((p) => (
            <div key={p.id} className="border rounded-lg p-4 bg-slate-50">
              {p.imagenUrl && (
                <img src={p.imagenUrl} alt={p.nombre} className="w-full h-32 object-cover rounded mb-3" />
              )}
              <div className="flex justify-between items-start">
                <h3 className="font-semibold">{p.nombre}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${estadoColor[p.estado] || 'bg-slate-100 text-slate-600'}`}>
                  {p.estado}
                </span>
              </div>
              <p className="text-xs text-slate-500 italic">{p.especie}</p>
              <div className="mt-2 text-sm text-slate-600 space-y-1">
                <p>Lote: <span className="font-mono">{p.lote}</span></p>
                <p>Cantidad: {p.cantidad} · ${Number(p.precio).toLocaleString()}</p>
                <p>Siembra: {p.fechaSiembra}</p>
                {p.zona && <p>Zona: {p.zona.nombre || p.zona}</p>}
              </div>
              <div className="mt-3 flex gap-2">
                <button onClick={() => openEdit(p)} className="text-xs px-3 py-1 rounded border border-slate-300 hover:bg-slate-100">{t('common.edit')}</button>
                <button onClick={() => handleDelete(p.id)} className="text-xs px-3 py-1 rounded border border-red-200 text-red-600 hover:bg-red-50">{t('common.delete')}</button>
              </div>
            </div>
          ))}
          {items.length === 0 && <p className="text-slate-400 text-sm col-span-3">Sin plantas registradas.</p>}
        </div>
      )}

      {modal && (
        <Modal title={modal === 'edit' ? 'Editar Planta' : 'Nueva Planta'} onClose={closeModal}>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.nombre')} *</label>
                <input name="nombre" value={form.nombre} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.especie')}</label>
                <input name="especie" value={form.especie || ''} onChange={handleChange} className={inp} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.lote')} *</label>
                <input name="lote" value={form.lote} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.estado')}</label>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.cantidad')}</label>
                <input type="number" name="cantidad" value={form.cantidad} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.precio')}</label>
                <input type="number" name="precio" value={form.precio} onChange={handleChange} className={inp} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.fechaSiembra')}</label>
                <input type="date" name="fechaSiembra" value={form.fechaSiembra || ''} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('planta.fechaEstimadaVenta')}</label>
                <input type="date" name="fechaEstimadaVenta" value={form.fechaEstimadaVenta || ''} onChange={handleChange} className={inp} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('planta.zona')}</label>
              <select name="zonaId" value={form.zonaId} onChange={handleChange} className={inp}>
                <option value="">— Seleccionar zona —</option>
                {zonas.map((z) => <option key={z.id} value={z.id}>{z.nombre}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('planta.descripcion')}</label>
              <textarea name="descripcion" value={form.descripcion || ''} onChange={handleChange} rows={2} className={inp} />
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
