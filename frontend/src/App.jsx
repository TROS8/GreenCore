import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './i18n/index.js'
import Navbar from './components/Navbar'
import AuthHandler from './auth/AuthHandler'
import { PrivateRoute } from './components/PrivateRoute'
import Dashboard from './components/Dashboard'
import { ZonaList } from './components/ZonaList'
import { SensorList } from './components/SensorList'
import { AlertaList } from './components/AlertaList'
import { PlantaList } from './components/PlantaList'
import { ClienteList } from './components/ClienteList'
import { VentaList } from './components/VentaList'
import { UsuarioList } from './components/UsuarioList'

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthHandler />
      <div className="min-h-screen bg-slate-100 flex flex-col">
        <Navbar />
        <main className="flex-1 container mx-auto p-6">
          <Routes>
            <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/zonas" element={<PrivateRoute><ZonaList /></PrivateRoute>} />
            <Route path="/plantas" element={<PrivateRoute><PlantaList /></PrivateRoute>} />
            <Route path="/sensores" element={<PrivateRoute><SensorList /></PrivateRoute>} />
            <Route path="/alertas" element={<PrivateRoute><AlertaList /></PrivateRoute>} />
            <Route path="/clientes" element={<PrivateRoute><ClienteList /></PrivateRoute>} />
            <Route path="/ventas" element={<PrivateRoute><VentaList /></PrivateRoute>} />
            <Route path="/usuarios" element={<PrivateRoute><UsuarioList /></PrivateRoute>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
