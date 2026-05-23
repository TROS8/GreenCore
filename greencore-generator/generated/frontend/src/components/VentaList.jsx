import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { getAllVentas } from '../services/ventaService';

export function VentaList() {
  const { t } = useTranslation();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllVentas()
      .then((data) => setItems(data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <h2 className="text-xl font-semibold mb-4">{t('venta.title', 'Venta')}</h2>
      {loading ? (
        <div>{t('common.loading', 'Cargando...')}</div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {items.slice(0, 4).map((item) => (
              <div key={item.id} className="border rounded-lg p-4 bg-slate-50">
                <h3 className="font-semibold text-lg">{item.nombre || item.codigo || item.email || `ID ${item.id}`}</h3>
                <p className="text-sm text-slate-600">{item.descripcion || item.mensaje || item.unidad || ''}</p>
              </div>
            ))}
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={items.map((item, index) => ({ name: index + 1, value: item.valorActual || item.cantidad || item.precio || 0 }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}