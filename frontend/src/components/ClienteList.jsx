/**
 * GreenCore — Vista CRUD de clientes compradores.
 *
 * @module components/ClienteList
 * @version 2.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllClientes, createCliente, updateCliente, deleteCliente } from '../services/clienteService'
import { Modal } from './Modal'
import {
  inp, Spinner, EmptyState, PageHeader,
  Field, FormActions, ErrorBanner, StatusBadge, ActionBtn,
} from './ui'

const EMPTY = { nombre: '', email: '', telefono: '', ciudad: '', activo: true }

export function ClienteList() {
  const { t } = useTranslation()
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [modal,   setModal]   = useState(null)
  const [form,    setForm]    = useState(EMPTY)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState(null)

  const reload = () => getAllClientes().then(setItems).finally(() => setLoading(false))
  useEffect(() => { reload() }, [])

  const openCreate = () => { setForm(EMPTY);    setError(null); setModal('create') }
  const openEdit   = (c) => { setForm({ ...c }); setError(null); setModal('edit')   }
  const closeModal = ()  => { setModal(null);   setError(null) }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setForm((f) => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSave = async () => {
    setSaving(true); setError(null)
    try {
      if (modal === 'edit') await updateCliente(form.id, form)
      else                  await createCliente(form)
      closeModal(); reload()
    } catch (err) {
      setError(err.response?.data?.message || 'Error al guardar.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(t('cliente.confirmDelete'))) return
    await deleteCliente(id); reload()
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={t('cliente.title')}
        count={items.length}
        onNew={openCreate}
        btnLabel={t('cliente.new')}
      />

      {loading ? <Spinner /> : items.length === 0 ? (
        <EmptyState icon="👥" message={t('cliente.noData')} />
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  <th className="px-5 py-3">{t('cliente.nombre')}</th>
                  <th className="px-5 py-3">{t('cliente.email')}</th>
                  <th className="px-5 py-3 hidden sm:table-cell">{t('cliente.telefono')}</th>
                  <th className="px-5 py-3 hidden md:table-cell">{t('cliente.ciudad')}</th>
                  <th className="px-5 py-3">{t('cliente.activo')}</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {items.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3 font-semibold text-slate-800">{c.nombre}</td>
                    <td className="px-5 py-3 text-slate-500">{c.email}</td>
                    <td className="px-5 py-3 text-slate-500 hidden sm:table-cell">{c.telefono || '—'}</td>
                    <td className="px-5 py-3 text-slate-500 hidden md:table-cell">{c.ciudad || '—'}</td>
                    <td className="px-5 py-3">
                      <StatusBadge
                        active={c.activo}
                        activeLabel={t('common.active')}
                        inactiveLabel={t('common.inactive')}
                      />
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex gap-2">
                        <ActionBtn onClick={() => openEdit(c)}>{t('common.edit')}</ActionBtn>
                        <ActionBtn onClick={() => handleDelete(c.id)} variant="danger">{t('common.delete')}</ActionBtn>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {modal && (
        <Modal
          title={modal === 'edit' ? t('cliente.edit') : t('cliente.new')}
          onClose={closeModal}
        >
          <div className="space-y-3">
            <Field label={t('cliente.nombre')} required>
              <input name="nombre" value={form.nombre} onChange={handleChange} className={inp} />
            </Field>
            <Field label={t('cliente.email')} required>
              <input type="email" name="email" value={form.email} onChange={handleChange} className={inp} />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label={t('cliente.telefono')}>
                <input name="telefono" value={form.telefono || ''} onChange={handleChange} className={inp} />
              </Field>
              <Field label={t('cliente.ciudad')}>
                <input name="ciudad" value={form.ciudad || ''} onChange={handleChange} className={inp} />
              </Field>
            </div>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input type="checkbox" name="activo" checked={form.activo} onChange={handleChange}
                className="w-4 h-4 accent-emerald-600" />
              <span className="text-sm font-semibold text-slate-700">{t('cliente.activo')}</span>
            </label>
            <ErrorBanner message={error} />
            <FormActions onCancel={closeModal} onSave={handleSave} saving={saving}
              saveLabel={t('common.save')} cancelLabel={t('common.cancel')} />
          </div>
        </Modal>
      )}
    </div>
  )
}
