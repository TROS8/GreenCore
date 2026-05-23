import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

// Remove stale sessionExpired flag from any previous persist version
try {
  const raw = localStorage.getItem('greencore-store')
  if (raw) {
    const parsed = JSON.parse(raw)
    if (parsed?.state?.sessionExpired !== undefined) {
      delete parsed.state.sessionExpired
      localStorage.setItem('greencore-store', JSON.stringify(parsed))
    }
  }
} catch (_) {}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
