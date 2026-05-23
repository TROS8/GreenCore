/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista CRUD de clientes compradores del invernadero.
 *
 * @module components/ClienteList
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllClientes, createCliente, updateCliente, deleteCliente } from '../services/clienteService'
import { Modal } from './Modal'

const EMPTY = { nombre: '', email: '', telefono: '', ciudad: '', activo: true }
const inp = 'mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500'

export function ClienteList() {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const reload = () => getAllClientes().then(setItems).finally(() => setLoading(false))
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY); setError(null); setModal('create') }
  const openEdit = (c) => { setForm({ ...c }); setError(null); setModal('edit') }
  const closeModal = () => { setModal(null); setError(null) }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      if (modal === 'edit') await updateCliente(form.id, form)
      else await createCliente(form)
      closeModal()
      reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar. Verifica los datos e intenta de nuevo.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este cliente?')) return
    await deleteCliente(id)
    reload()
  }

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">{t('cliente.title')}</h2>
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
                <th className="pb-2 pr-4">{t('cliente.nombre')}</th>
                <th className="pb-2 pr-4">{t('cliente.email')}</th>
                <th className="pb-2 pr-4">{t('cliente.telefono')}</th>
                <th className="pb-2 pr-4">{t('cliente.ciudad')}</th>
                <th className="pb-2 pr-4">{t('cliente.activo')}</th>
                <th className="pb-2"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id} className="border-b last:border-0 hover:bg-slate-50">
                  <td className="py-2 pr-4 font-medium">{c.nombre}</td>
                  <td className="py-2 pr-4 text-slate-600">{c.email}</td>
                  <td className="py-2 pr-4 text-slate-600">{c.telefono || '—'}</td>
                  <td className="py-2 pr-4 text-slate-600">{c.ciudad || '—'}</td>
                  <td className="py-2 pr-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${c.activo ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-500'}`}>
                      {c.activo ? t('common.active') : t('common.inactive')}
                    </span>
                  </td>
                  <td className="py-2">
                    <div className="flex gap-2">
                      <button onClick={() => openEdit(c)} className="text-xs px-2 py-1 rounded border border-slate-300 hover:bg-slate-100">{t('common.edit')}</button>
                      <button onClick={() => handleDelete(c.id)} className="text-xs px-2 py-1 rounded border border-red-200 text-red-600 hover:bg-red-50">{t('common.delete')}</button>
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={6} className="py-4 text-slate-400">Sin clientes registrados.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <Modal title={modal === 'edit' ? 'Editar Cliente' : 'Nuevo Cliente'} onClose={closeModal}>
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-slate-700">{t('cliente.nombre')} *</label>
              <input name="nombre" value={form.nombre} onChange={handleChange} className={inp} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">{t('cliente.email')} *</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} className={inp} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium text-slate-700">{t('cliente.telefono')}</label>
                <input name="telefono" value={form.telefono || ''} onChange={handleChange} className={inp} />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">{t('cliente.ciudad')}</label>
                <input name="ciudad" value={form.ciudad || ''} onChange={handleChange} className={inp} />
              </div>
            </div>
            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" name="activo" checked={form.activo} onChange={handleChange} className="w-4 h-4 accent-emerald-600" />
                <span className="text-sm font-medium text-slate-700">{t('cliente.activo')}</span>
              </label>
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
