/**
 * GreenCore — Helpers de UI reutilizables.
 * Spinner, EmptyState, PageHeader, Btn, Field, FormActions.
 *
 * @module components/ui
 * @version 1.0.0
 */
import React from 'react'
import { useTranslation } from 'react-i18next'

export const inp = 'mt-1 w-full border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 bg-white transition'

export function Spinner() {
  const { t } = useTranslation()
  return (
    <div className="flex items-center justify-center py-16 text-slate-400 gap-2">
      <svg className="animate-spin h-6 w-6 text-emerald-500" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
      </svg>
      <span className="text-sm">{t('common.loading')}</span>
    </div>
  )
}

export function EmptyState({ icon = '📋', message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-2">
      <span className="text-5xl">{icon}</span>
      <p className="text-sm font-medium">{message}</p>
    </div>
  )
}

export function PageHeader({ title, count, onNew, btnLabel }) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-xl font-bold text-slate-800">{title}</h2>
        {count != null && (
          <p className="text-sm text-slate-400 mt-0.5">{count} registro{count !== 1 ? 's' : ''}</p>
        )}
      </div>
      {onNew && (
        <button
          onClick={onNew}
          className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 text-white rounded-xl text-sm font-semibold shadow-sm hover:shadow-md transition-all"
        >
          {btnLabel}
        </button>
      )}
    </div>
  )
}

export function Field({ label, required, children }) {
  return (
    <div>
      <label className="text-sm font-semibold text-slate-700">
        {label}{required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      {children}
    </div>
  )
}

export function FormActions({ onCancel, onSave, saving, saveLabel = 'Guardar', cancelLabel = 'Cancelar' }) {
  return (
    <div className="flex justify-end gap-2 pt-3 border-t border-slate-100 mt-2">
      <button
        onClick={onCancel}
        className="px-4 py-2 text-sm rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
      >
        {cancelLabel}
      </button>
      <button
        onClick={onSave}
        disabled={saving}
        className="px-4 py-2 text-sm rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 text-white font-semibold shadow-sm hover:shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {saving ? '...' : saveLabel}
      </button>
    </div>
  )
}

export function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
      {message}
    </p>
  )
}

export function StatusBadge({ active, activeLabel = 'Activo', inactiveLabel = 'Inactivo' }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium
      ${active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
      {active ? activeLabel : inactiveLabel}
    </span>
  )
}

export function ActionBtn({ onClick, variant = 'secondary', children, disabled }) {
  const cls = {
    secondary: 'text-xs px-3 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition border border-slate-200',
    danger:    'text-xs px-3 py-1 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition border border-red-200',
    primary:   'text-xs px-3 py-1 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition',
  }
  return (
    <button onClick={onClick} disabled={disabled} className={`${cls[variant]} disabled:opacity-50`}>
      {children}
    </button>
  )
}
