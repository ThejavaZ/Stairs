import { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import { getCameras, createCamera, updateCamera, deleteCamera } from '../api/api';
import { Video, Plus, Edit, Trash2, Eye } from 'lucide-react';
import CameraStream from '../components/CameraStream';

interface Camera {
  id: number;
  name: string;
  ip_address: string;
  port: number;
  username: string;
  password?: string;
  is_active: boolean;
}

interface CameraModalProps {
  camera: Camera | null;
  onClose: () => void;
  onSave: (cameraData: any) => void;
}

const CameraModal: React.FC<CameraModalProps> = ({ camera, onClose, onSave }) => {
  const [formData, setFormData] = useState(
    camera || {
      name: '',
      ip_address: '',
      port: '',
      username: '',
      password: '',
      is_active: true,
    }
  );

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-2xl font-bold text-slate-800 mb-6">{camera ? 'Editar' : 'Añadir'} Cámara</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Nombre (ej. Escalera Principal)" required className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="text" name="ip_address" value={formData.ip_address} onChange={handleChange} placeholder="Dirección IP (ej. 192.168.1.100)" required className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="number" name="port" value={formData.port} onChange={handleChange} placeholder="Puerto (ej. 554)" required className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="text" name="username" value={formData.username} onChange={handleChange} placeholder="Usuario" required className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          <input type="password" name="password" value={formData.password} onChange={handleChange} placeholder="Contraseña" required className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          <label className="flex items-center space-x-3">
            <input type="checkbox" name="is_active" checked={formData.is_active} onChange={handleChange} className="h-5 w-5 rounded text-blue-600 focus:ring-blue-500" />
            <span className="text-slate-700">Activa</span>
          </label>
          <div className="flex justify-end space-x-4 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Cameras = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const data = await getCameras();
      setCameras(data);
    } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  };

  useEffect(() => { fetchCameras(); }, []);

  const handleSave = async (cameraData: any) => {
    try {
      if (editingCamera) {
        await updateCamera(editingCamera.id, cameraData);
      } else {
        await createCamera(cameraData);
      }
      fetchCameras();
      setIsModalOpen(false);
      setEditingCamera(null);
    } catch (err: any) { alert(`Error al guardar: ${err.message}`); }
  };

  const handleDelete = async (cameraId: number) => {
    if (window.confirm('¿Estás seguro? Esta acción es irreversible.')) {
      try {
        await deleteCamera(cameraId);
        fetchCameras();
      } catch (err: any) { alert(`Error al eliminar: ${err.message}`); }
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">Gestión de Cámaras</h1>
        <button onClick={() => { setEditingCamera(null); setIsModalOpen(true); }} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-sm">
          <Plus className="mr-2" /> Añadir Cámara
        </button>
      </div>

      {loading && <p className="text-slate-500">Cargando cámaras...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {selectedCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-40" onClick={() => setSelectedCamera(null)}>
          <div className="w-full max-w-4xl p-4" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            <CameraStream cameraId={selectedCamera.id} />
          </div>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <ul className="space-y-4">
          {cameras.map((cam: Camera) => (
            <li key={cam.id} className="flex flex-col md:flex-row justify-between items-start md:items-center p-4 border border-slate-200 rounded-lg hover:bg-slate-50">
              <div className="flex items-center mb-2 md:mb-0">
                <Video className={`mr-4 ${cam.is_active ? 'text-green-500' : 'text-slate-400'}`} size={32} />
                <div>
                  <p className="font-bold text-lg text-slate-800">{cam.name}</p>
                  <p className="text-sm text-slate-500">{cam.ip_address}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button onClick={() => setSelectedCamera(cam)} disabled={!cam.is_active} className={`flex items-center px-3 py-2 text-sm rounded ${!cam.is_active ? 'bg-slate-300 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'} text-white shadow-sm`}>
                  <Eye className="mr-1" size={16}/> Ver Cámara
                </button>
                <button onClick={() => { setEditingCamera(cam); setIsModalOpen(true); }} className="p-2 text-slate-500 hover:text-blue-600"><Edit /></button>
                <button onClick={() => handleDelete(cam.id)} className="p-2 text-slate-500 hover:text-red-600"><Trash2 /></button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {isModalOpen && <CameraModal camera={editingCamera} onClose={() => setIsModalOpen(false)} onSave={handleSave} />}
    </div>
  );
};

export default Cameras;