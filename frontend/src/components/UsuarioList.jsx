/**
 * GreenCore — Sistema de gestion de invernadero
 * Vista de administracion de usuarios. El rol ADMIN puede cambiar roles
 * y eliminar usuarios directamente desde esta pantalla.
 *
 * @module components/UsuarioList
 * @version 1.0.0
 */
import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { getAllUsuarios, updateUsuario, deleteUsuario } from '../services/usuarioService'
import { useStore } from '../store/useStore'

const ROLES = ['ADMIN', 'OPERARIO', 'VISUALIZADOR']

const ROLE_COLORS = {
  ADMIN:        'bg-red-100 text-red-700 border border-red-200',
  OPERARIO:     'bg-blue-100 text-blue-700 border border-blue-200',
  VISUALIZADOR: 'bg-slate-100 text-slate-600 border border-slate-200',
}

export function UsuarioList() {
  const { t }  = useTranslation()
  const role   = useStore((s) => s.role)
  const myEmail = useStore((s) => s.user?.email)
  const isAdmin = role === 'ADMIN'

  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(null)   // id del usuario en proceso
  const [confirm, setConfirm] = useState(null)   // id a eliminar (modal de confirmacion)

  const reload = () => {
    setLoading(true)
    getAllUsuarios().then(setItems).finally(() => setLoading(false))
  }

  useEffect(() => { reload() }, [])

  const handleRoleChange = async (usuario, newRole) => {
    if (!isAdmin || newRole === usuario.rol) return
    setSaving(usuario.id)
    try {
      await updateUsuario(usuario.id, { ...usuario, rol: newRole })
      setItems(prev => prev.map(u => u.id === usuario.id ? { ...u, rol: newRole } : u))
    } catch {
      alert('Error al actualizar rol')
    } finally {
      setSaving(null)
    }
  }

  const handleDelete = async (id) => {
    setSaving(id)
    setConfirm(null)
    try {
      await deleteUsuario(id)
      setItems(prev => prev.filter(u => u.id !== id))
    } catch {
      alert('Error al eliminar usuario')
    } finally {
      setSaving(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Cabecera */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800">{t('usuario.title')}</h2>
          <p className="text-sm text-slate-500 mt-0.5">
            {isAdmin
              ? 'Gestiona roles y accesos de cada usuario.'
              : 'Usuarios registrados en el sistema.'}
          </p>
        </div>
        <span className="text-sm text-slate-400">{items.length} usuario{items.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Banner info para no-admin */}
      {!isAdmin && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3 text-blue-700 text-sm">
          Solo el rol <strong>ADMIN</strong> puede cambiar roles o eliminar usuarios.
        </div>
      )}

      {loading ? (
        <div className="flex items-center gap-2 text-slate-400 py-8 justify-center">
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
          </svg>
          <span>{t('common.loading')}</span>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left px-4 py-3 font-semibold text-slate-600">Usuario</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600">Email</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600">Rol</th>
                <th className="text-left px-4 py-3 font-semibold text-slate-600">Estado</th>
                {isAdmin && <th className="px-4 py-3 font-semibold text-slate-600 text-right">Acciones</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((u) => {
                const isSelf    = u.email === myEmail
                const isBusy    = saving === u.id
                return (
                  <tr key={u.id} className={`transition-colors ${isSelf ? 'bg-emerald-50/50' : 'hover:bg-slate-50'}`}>
                    {/* Avatar + nombre */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {u.fotoPerfil ? (
                          <img src={u.fotoPerfil} alt={u.nombre}
                               className="w-8 h-8 rounded-full object-cover ring-1 ring-slate-200" />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 font-bold text-xs flex items-center justify-center">
                            {u.nombre?.[0]?.toUpperCase()}
                          </div>
                        )}
                        <div>
                          <span className="font-medium text-slate-800">{u.nombre}</span>
                          {isSelf && <span className="ml-1.5 text-xs text-emerald-600 font-semibold">(tú)</span>}
                        </div>
                      </div>
                    </td>

                    {/* Email */}
                    <td className="px-4 py-3 text-slate-500">{u.email}</td>

                    {/* Rol */}
                    <td className="px-4 py-3">
                      {isAdmin && !isSelf ? (
                        <select
                          value={u.rol}
                          disabled={isBusy}
                          onChange={(e) => handleRoleChange(u, e.target.value)}
                          className={`text-xs px-2 py-1 rounded-lg border font-semibold cursor-pointer
                                      focus:outline-none focus:ring-2 focus:ring-emerald-300 transition
                                      ${ROLE_COLORS[u.rol] || 'bg-slate-100 text-slate-600'}
                                      ${isBusy ? 'opacity-50 cursor-wait' : ''}`}
                        >
                          {ROLES.map(r => (
                            <option key={r} value={r}>{r}</option>
                          ))}
                        </select>
                      ) : (
                        <span className={`text-xs px-2 py-1 rounded-full font-semibold ${ROLE_COLORS[u.rol] || 'bg-slate-100'}`}>
                          {u.rol}
                        </span>
                      )}
                    </td>

                    {/* Estado */}
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium
                        ${u.activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                        {u.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>

                    {/* Acciones ADMIN */}
                    {isAdmin && (
                      <td className="px-4 py-3 text-right">
                        {!isSelf ? (
                          <button
                            onClick={() => setConfirm(u.id)}
                            disabled={isBusy}
                            className="text-xs px-3 py-1 rounded-lg bg-red-50 text-red-600 hover:bg-red-100
                                       border border-red-200 transition disabled:opacity-40 disabled:cursor-wait"
                          >
                            {isBusy ? '...' : 'Eliminar'}
                          </button>
                        ) : (
                          <span className="text-xs text-slate-300">—</span>
                        )}
                      </td>
                    )}
                  </tr>
                )
              })}
              {items.length === 0 && (
                <tr>
                  <td colSpan={isAdmin ? 5 : 4} className="px-4 py-8 text-center text-slate-400">
                    Sin usuarios registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal de confirmación de eliminación */}
      {confirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-bold text-slate-800 mb-2">Eliminar usuario</h3>
            <p className="text-slate-600 text-sm mb-6">
              Esta accion es irreversible. El usuario no podra volver a acceder hasta que inicie sesion de nuevo con Google.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setConfirm(null)}
                className="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-sm transition"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleDelete(confirm)}
                className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 text-sm font-semibold transition"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
