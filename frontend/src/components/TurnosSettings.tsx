import { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import { getTurnos, updateTurnos } from '../api/api';
import { Save } from 'lucide-react';

interface Turno {
  inicio: string;
  fin: string;
}

interface Turnos {
  [key: string]: Turno;
}

const TurnosSettings = () => {
  const [turnos, setTurnos] = useState<Turnos | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchTurnos = async () => {
      try {
        setLoading(true);
        const data = await getTurnos();
        setTurnos(data);
      } catch (err: any) {
        setError('No se pudo cargar la configuración de turnos.');
      } finally {
        setLoading(false);
      }
    };
    fetchTurnos();
  }, []);

  const handleChange = (turno: string, field: string, value: string) => {
    setTurnos(prev => {
        if (!prev) return null;
        return {
            ...prev,
            [turno]: { ...prev[turno], [field]: value },
        }
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateTurnos(turnos);
      setSuccess('¡Horarios de turnos guardados con éxito!');
    } catch (err: any) {
      setError(`Error al guardar: ${err.message}`);
    } finally {
      setSaving(false);
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  if (loading) {
    return <div className="text-slate-500">Cargando configuración de turnos...</div>;
  }

  if (error && !turnos) {
      return <div className="text-red-500">{error}</div>
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-sm border border-slate-200 max-w-2xl mx-auto space-y-6 mt-8">
      <h2 className="text-xl font-semibold text-slate-800 border-b border-slate-200 pb-4">Horarios de Turnos</h2>
      {turnos && Object.keys(turnos).map(turnoKey => (
        <div key={turnoKey} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <label className="font-medium text-slate-700">
            {`Turno ${turnoKey.split('_')[1]}`}
          </label>
          <div className="col-span-2 grid grid-cols-2 gap-4">
            <div>
              <label htmlFor={`${turnoKey}_inicio`} className="block text-sm text-slate-600">Inicio</label>
              <input 
                type="time" 
                id={`${turnoKey}_inicio`} 
                value={turnos[turnoKey].inicio}
                onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(turnoKey, 'inicio', e.target.value)}
                className="mt-1 block w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor={`${turnoKey}_fin`} className="block text-sm text-slate-600">Fin</label>
              <input 
                type="time" 
                id={`${turnoKey}_fin`} 
                value={turnos[turnoKey].fin}
                onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(turnoKey, 'fin', e.target.value)}
                className="mt-1 block w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      ))}
      <div className="pt-4 flex items-center justify-end">
        {success && <p className="text-green-600 mr-4">{success}</p>}
        {error && <p className="text-red-600 mr-4">{error}</p>}
        <button type="submit" disabled={saving} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 shadow-sm">
          <Save className="mr-2" size={18}/>
          {saving ? 'Guardando...' : 'Guardar Horarios'}
        </button>
      </div>
    </form>
  );
};

export default TurnosSettings;
