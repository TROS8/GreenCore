import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllVentas, createVenta } from '../services/ventaService'
import { getAllPlantas } from '../services/plantaService'
import { getAllClientes } from '../services/clienteService'
import { Modal } from './Modal'

const estadoColor = {
  PENDIENTE: 'bg-yellow-100 text-yellow-700',
  COMPLETADA: 'bg-green-100 text-green-700',
  ANULADA: 'bg-red-100 text-red-500',
}

const ESTADOS = ['PENDIENTE', 'COMPLETADA', 'ANULADA']
const inp = 'mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500'

const EMPTY = {
  numeroFactura: '', cantidad: 1, precioUnitario: 0,
  total: 0, estado: 'PENDIENTE', notas: '',
  fecha: new Date().toISOString().slice(0, 16),
  plantaId: '', clienteId: '',
}

export function VentaList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [plantas, setPlantas] = useState([])
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = () => {
    Promise.all([getAllVentas(), getAllPlantas(), getAllClientes()])
      .then(([v, p, c]) => { setItems(v); setPlantas(p); setClientes(c) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal(true) }
  const closeModal = () => { setModal(false); setError(null) }

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => {
      const updated = { ...f, [name]: value }
      if (name === 'cantidad' || name === 'precioUnitario') {
        const q = parseFloat(name === 'cantidad' ? value : f.cantidad) || 0
        const p = parseFloat(name === 'precioUnitario' ? value : f.precioUnitario) || 0
        updated.total = (q * p).toFixed(2)
      }
      return updated
    })
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      await createVenta({
        ...form,
        planta: form.plantaId ? { id: parseInt(form.plantaId) } : null,
        cliente: form.clienteId ? { id: parseInt(form.clienteId) } : null,
      })
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar. Verifica los datos e intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{t('venta.title')}</h2>
        <button onClick={openCreate} className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
          + {t('common.create')}
        </button>
      </div>

      {loading ? (
        <p className="text-slate-500">{t('common.loading')}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b text-left text-slate-500 uppercase text-xs tracking-wide">
                <th className="pb-2 pr-4">{t('venta.numeroFactura')}</th>
                <th className="pb-2 pr-4">{t('venta.planta')}</th>
                <th className="pb-2 pr-4">{t('venta.cliente')}</th>
                <th className="pb-2 pr-4">{t('venta.cantidad')}</th>
                <th className="pb-2 pr-4">{t('venta.total')}</th>
                <th className="pb-2 pr-4">{t('venta.fecha')}</th>
                <th className="pb-2">{t('venta.estado')}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((v) => (
                <tr key={v.id} className="border-b last:border-0 hover:bg-slate-50">
                  <td className="py-2 pr-4 font-mono text-xs">{v.numeroFactura}</td>
                  <td className="py-2 pr-4">{v.planta?.nombre || '—'}</td>
                  <td className="py-2 pr-4">{v.cliente?.nombre || '—'}</td>
                  <td className="py-2 pr-4">{v.cantidad}</td>
                  <td className="py-2 pr-4 font-semibold">${Number(v.total).toLocaleString()}</td>
                  <td className="py-2 pr-4 text-slate-500 text-xs">{new Date(v.fecha).toLocaleDateString()}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${estadoColor[v.estado] || 'bg-slate-100'}`}>
                      {v.estado}
                    </span>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={7} className="py-4 text-slate-400">Sin ventas registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title="Nueva Venta" onClose={closeModal}>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('venta.numeroFactura')} *</label>
                <input name="numeroFactura" value={form.numeroFactura} onChange={handleChange} className={inp} placeholder="FAC-001" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('venta.estado')}</label>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('venta.planta')} *</label>
              <select name="plantaId" value={form.plantaId} onChange={handleChange} className={inp}>
                <option value="">— Seleccionar planta —</option>
                {plantas.map((p) => <option key={p.id} value={p.id}>{p.nombre} ({p.lote})</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('venta.cliente')} *</label>
              <select name="clienteId" value={form.clienteId} onChange={handleChange} className={inp}>
                <option value="">— Seleccionar cliente —</option>
                {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('venta.cantidad')}</label>
                <input type="number" name="cantidad" value={form.cantidad} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('venta.precioUnitario')}</label>
                <input type="number" name="precioUnitario" value={form.precioUnitario} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('venta.total')}</label>
                <input type="number" name="total" value={form.total} readOnly className={`${inp} bg-slate-50`} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('venta.fecha')}</label>
              <input type="datetime-local" name="fecha" value={form.fecha} onChange={handleChange} className={inp} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('venta.notas')}</label>
              <textarea name="notas" value={form.notas || ''} onChange={handleChange} rows={2} className={inp} />
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
