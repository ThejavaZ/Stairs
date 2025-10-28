import { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import { getSettings, updateSetting } from '../api/api';
import { Save } from 'lucide-react';
import TurnosSettings from '../components/TurnosSettings';

interface SettingsData {
    [key: string]: string;
}

const Settings = () => {
  const [settings, setSettings] = useState<SettingsData>({});
  const [initialSettings, setInitialSettings] = useState<SettingsData>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await getSettings();
        setSettings(data);
        setInitialSettings(data);
      } catch (err: any) {
        setError('No se pudo cargar la configuración.');
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? (checked ? 'true' : 'false') : value;
    setSettings((prev) => ({ ...prev, [name]: val }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const changedSettings = Object.keys(settings).filter(
        (key) => settings[key] !== initialSettings[key]
      );

      if (changedSettings.length === 0) {
        setSuccess('No hay cambios que guardar.');
        return;
      }

      await Promise.all(
        changedSettings.map(key => updateSetting(key, settings[key]))
      );
      
      setInitialSettings(settings);
      setSuccess('¡Configuración guardada con éxito!');
    } catch (err: any) {
      setError(`Error al guardar: ${err.message}`);
    } finally {
      setSaving(false);
      setTimeout(() => setSuccess(''), 3000);
    }
  };

  const renderInput = (key: string, value: string) => {
    const isBoolean = value === 'true' || value === 'false';
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

    if (isBoolean) {
      return (
        <div key={key} className="flex items-center justify-between py-2">
          <label htmlFor={key} className="font-medium text-slate-700">{label}</label>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
                type="checkbox" 
                id={key} 
                name={key} 
                checked={value === 'true'} 
                onChange={handleChange} 
                className="sr-only peer" 
            />
            <div className="w-11 h-6 bg-slate-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      );
    }

    return (
      <div key={key}>
        <label htmlFor={key} className="block text-sm font-medium text-slate-700">{label}</label>
        <input 
            type="number" 
            step="0.05" 
            id={key} 
            name={key} 
            value={value} 
            onChange={handleChange} 
            className="mt-1 block w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500"
        />
      </div>
    );
  };

  if (loading) {
    return <div className="text-slate-500">Cargando configuración...</div>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-slate-800">Configuración del Sistema</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-sm border border-slate-200 max-w-2xl mx-auto space-y-6">
        <h2 className="text-xl font-semibold text-slate-800 border-b border-slate-200 pb-4">Parámetros de Detección</h2>
        {Object.keys(settings).map(key => renderInput(key, settings[key]))}
        
        <div className="pt-4 flex items-center justify-end">
            {success && <p className="text-green-600 mr-4">{success}</p>}
            {error && <p className="text-red-600 mr-4">{error}</p>}
            <button type="submit" disabled={saving} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 shadow-sm">
                <Save className="mr-2" size={18}/>
                {saving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
        </div>
      </form>

      <TurnosSettings />

    </div>
  );
};

export default Settings;
