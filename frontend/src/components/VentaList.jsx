/**
 * GreenCore — Vista de registro y consulta de ventas de plantas.
 *
 * @module components/VentaList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllVentas, createVenta } from '../services/ventaService'
import { getAllPlantas } from '../services/plantaService'
import { getAllClientes } from '../services/clienteService'
import { Modal } from './Modal'
import {
  inp, Spinner, EmptyState, PageHeader,
  Field, FormActions, ErrorBanner,
} from './ui'

const ESTADO_COLOR = {
  PENDIENTE:  'bg-yellow-100 text-yellow-700',
  COMPLETADA: 'bg-green-100  text-green-700',
  ANULADA:    'bg-red-100    text-red-500',
}

const ESTADOS = ['PENDIENTE', 'COMPLETADA', 'ANULADA']

const EMPTY = {
  numeroFactura: '', cantidad: 1, precioUnitario: 0,
  total: 0, estado: 'PENDIENTE', notas: '',
  fecha: new Date().toISOString().slice(0, 16),
  plantaId: '', clienteId: '',
}

export function VentaList() {
  const { t } = useTranslation()
  const [items,    setItems]    = useState([])
  const [plantas,  setPlantas]  = useState([])
  const [clientes, setClientes] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [modal,    setModal]    = useState(false)
  const [form,     setForm]     = useState(EMPTY)
  const [saving,   setSaving]   = useState(false)
  const [error,    setError]    = useState(null)

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
    setSaving(true); setError(null)
    try {
      await createVenta({
        ...form,
        planta:  form.plantaId  ? { id: parseInt(form.plantaId) }  : null,
        cliente: form.clienteId ? { id: parseInt(form.clienteId) } : null,
      })
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const totalVentas = items.reduce((acc, v) => acc + Number(v.total || 0), 0)

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('venta.title')}
        count={items.length}
        onNew={openCreate}
        btnLabel={t('venta.new')}
      />

      {/* Resumen rápido */}
      {items.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {[
            { label: t('venta.estado') + ' — PENDIENTE',  value: items.filter((v) => v.estado === 'PENDIENTE').length,  color: 'text-yellow-600' },
            { label: t('venta.estado') + ' — COMPLETADA', value: items.filter((v) => v.estado === 'COMPLETADA').length, color: 'text-green-600'  },
            { label: t('venta.totalFacturado'), value: `$${totalVentas.toLocaleString()}`, color: 'text-emerald-700' },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-4 py-3">
              <p className="text-xs text-slate-400 font-medium">{kpi.label}</p>
              <p className={`text-2xl font-extrabold mt-0.5 ${kpi.color}`}>{kpi.value}</p>
            </div>
          ))}
        </div>
      )}

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="🛒" message={t('venta.noData')} />
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  <th className="px-5 py-3">{t('venta.numeroFactura')}</th>
                  <th className="px-5 py-3">{t('venta.planta')}</th>
                  <th className="px-5 py-3 hidden md:table-cell">{t('venta.cliente')}</th>
                  <th className="px-5 py-3">{t('venta.cantidad')}</th>
                  <th className="px-5 py-3">{t('venta.total')}</th>
                  <th className="px-5 py-3 hidden sm:table-cell">{t('venta.fecha')}</th>
                  <th className="px-5 py-3">{t('venta.estado')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {items.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3 font-mono text-xs text-slate-600">{v.numeroFactura}</td>
                    <td className="px-5 py-3 font-medium text-slate-800">{v.planta?.nombre || '—'}</td>
                    <td className="px-5 py-3 text-slate-500 hidden md:table-cell">{v.cliente?.nombre || '—'}</td>
                    <td className="px-5 py-3 text-slate-600">{v.cantidad}</td>
                    <td className="px-5 py-3 font-bold text-emerald-700">${Number(v.total).toLocaleString()}</td>
                    <td className="px-5 py-3 text-slate-400 text-xs hidden sm:table-cell">
                      {new Date(v.fecha).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_COLOR[v.estado] || 'bg-slate-100 text-slate-600'}`}>
                        {v.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modal && (
        <Modal title={t('venta.new')} onClose={closeModal}>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('venta.numeroFactura')} required>
                <input name="numeroFactura" value={form.numeroFactura} onChange={handleChange}
                  className={inp} placeholder="FAC-001" />
              </Field>
              <Field label={t('venta.estado')}>
                <select name="estado" value={form.estado} onChange={handleChange} className={inp}>
                  {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                </select>
              </Field>
            </div>
            <Field label={t('venta.planta')} required>
              <select name="plantaId" value={form.plantaId} onChange={handleChange} className={inp}>
                <option value="">{t('common.selectPlant')}</option>
                {plantas.map((p) => <option key={p.id} value={p.id}>{p.nombre} ({p.lote})</option>)}
              </select>
            </Field>
            <Field label={t('venta.cliente')} required>
              <select name="clienteId" value={form.clienteId} onChange={handleChange} className={inp}>
                <option value="">{t('common.selectClient')}</option>
                {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </select>
            </Field>
            <div className="grid grid-cols-3 gap-3">
              <Field label={t('venta.cantidad')}>
                <input type="number" name="cantidad" value={form.cantidad} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('venta.precioUnitario')}>
                <input type="number" name="precioUnitario" value={form.precioUnitario} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('venta.total')}>
                <input type="number" name="total" value={form.total} readOnly
                  className={`${inp} bg-slate-50 cursor-default`} />
              </Field>
            </div>
            <Field label={t('venta.fecha')}>
              <input type="datetime-local" name="fecha" value={form.fecha} onChange={handleChange} className={inp} />
            </Field>
            <Field label={t('venta.notas')}>
              <textarea name="notas" value={form.notas || ''} onChange={handleChange} rows={2} className={inp} />
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
