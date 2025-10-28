import { useState, useEffect, ChangeEvent, ReactNode } from 'react';
import { getStatisticsSummary, listEvents, detectFromImage, deleteEvent } from '../api/api';
import { Users, AlertTriangle, Percent, Upload, Trash2, Calendar } from 'lucide-react';
import { BarChart } from '@mui/x-charts/BarChart';
import { PieChart } from '@mui/x-charts/PieChart';

interface StatCardProps {
    icon: ReactNode;
    title: string;
    value: string | number;
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value }) => (
  <div className={`bg-white p-6 rounded-lg shadow-sm flex items-center border border-slate-200`}>
    {icon}
    <div className="ml-4">
      <p className="text-sm text-slate-600">{title}</p>
      <p className="text-2xl font-bold text-slate-800">{value}</p>
    </div>
  </div>
);

// --- Chart Components ---
const FoulsByDayChart = ({ data }: { data: any[] }) => {
    if (!data || data.length === 0) return <div className="text-center text-slate-500 p-4">No hay datos de faltas para la última semana.</div>;
    return (
        <BarChart
            dataset={data}
            xAxis={[{ scaleType: 'band', dataKey: 'day' }]}
            series={[{ dataKey: 'total', label: 'Total Faltas', color: '#ef4444' }]}
            height={300}
        />
    );
};

const FoulsByShiftPieChart = ({ data }: { data: any }) => {
    if (!data) return <div className="text-center text-slate-500 p-4">No hay datos de turnos.</div>;

    const chartData = [
        { id: 0, value: data.turno_1?.faltas || 0, label: 'Turno 1' },
        { id: 1, value: data.turno_2?.faltas || 0, label: 'Turno 2' },
        { id: 2, value: data.turno_3?.faltas || 0, label: 'Turno 3' },
    ].filter(item => item.value > 0);

    if (chartData.length === 0) return <div className="text-center text-slate-500 p-4">No se registraron faltas por turno.</div>;

    return (
        <PieChart
            series={[
                {
                    data: chartData,
                    highlightScope: { faded: 'global', highlighted: 'item' },
                    fade: { innerRadius: 30, additionalRadius: -30, color: 'gray' },
                },
            ]}
            height={300}
        />
    );
};

// --- Helper Function ---
const processDailyFouls = (events: any[]) => {
    const dailyData: { [key: string]: { day: string; total: number } } = {};
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayKey = d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
        dailyData[dayKey] = { day: dayKey, total: 0 };
    }

    events.forEach(event => {
        const eventDate = new Date(event.fecha_hora);
        const dayKey = eventDate.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
        if (dailyData[dayKey]) {
            dailyData[dayKey].total += event.faltas;
        }
    });

    return Object.values(dailyData);
};


const Home = () => {
  const [stats, setStats] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [dailyFouls, setDailyFouls] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [detectionResult, setDetectionResult] = useState<any>(null);
  const [isDetecting, setIsDetecting] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const today = new Date();
      const sevenDaysAgo = new Date(today);
      sevenDaysAgo.setDate(today.getDate() - 7);

      const [statsData, recentEventsData, weeklyEventsData] = await Promise.all([
        getStatisticsSummary(7),
        listEvents(10),
        listEvents(1000, 0, sevenDaysAgo.toISOString(), today.toISOString()),
      ]);
      
      setStats(statsData);
      setEvents(recentEventsData);
      setDailyFouls(processDailyFouls(weeklyEventsData));
      setError('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsDetecting(true);
    setDetectionResult(null);
    setError('');
    try {
      const result = await detectFromImage(file);
      setDetectionResult(result);
      fetchData(); // Refresh data after detection
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsDetecting(false);
    }
  };

  const handleDeleteEvent = async (eventId: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este evento?')) {
      try {
        await deleteEvent(eventId);
        fetchData(); // Refresh list after deletion
      } catch (err: any) {
        setError(err.message);
      }
    }
  };

  if (loading && !stats) {
    return <div className="text-center p-8 text-slate-500">Cargando datos...</div>;
  }

  if (error && !stats) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="space-y-8">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={<Users size={40} className="text-blue-500" />} title="Total Empleados Detectados" value={stats?.total_empleados ?? 'N/A'} />
        <StatCard icon={<AlertTriangle size={40} className="text-red-500" />} title="Total Faltas EPP" value={stats?.total_faltas ?? 'N/A'} />
        <StatCard icon={<Percent size={40} className="text-amber-500" />} title="Tasa de Faltas" value={`${stats?.tasa_faltas ?? 0}%`} />
        <StatCard icon={<Calendar size={40} className="text-green-500" />} title="Eventos (Últimos 7 días)" value={stats?.total_eventos ?? 'N/A'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Events Table */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-800 mb-4">Eventos Recientes</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="p-3 font-semibold text-slate-600">Fecha y Hora</th>
                  <th className="p-3 font-semibold text-slate-600">Turno</th>
                  <th className="p-3 font-semibold text-slate-600">Empleados</th>
                  <th className="p-3 font-semibold text-slate-600">Faltas</th>
                  <th className="p-3 font-semibold text-slate-600">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {events.map(event => (
                  <tr key={event.id_evento} className="border-b border-slate-200 hover:bg-slate-50">
                    <td className="p-3 text-slate-700">{new Date(event.fecha_hora).toLocaleString()}</td>
                    <td className="p-3 text-slate-700">{event.turno}</td>
                    <td className="p-3 text-slate-700">{event.empleados}</td>
                    <td className="p-3 text-slate-700">{event.faltas}</td>
                    <td className="p-3">
                      <button onClick={() => handleDeleteEvent(event.id_evento)} className="text-slate-500 hover:text-red-600"><Trash2 size={18} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Image Detection */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <h2 className="text-xl font-bold text-slate-800 mb-4">Procesar Imagen</h2>
          <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-lg p-8">
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <Upload size={48} className="text-slate-400" />
              <span className="mt-2 text-sm text-slate-600">Selecciona una imagen</span>
              <input id="file-upload" type="file" className="hidden" accept="image/*" onChange={handleFileChange} disabled={isDetecting} />
            </label>
            {isDetecting && <p className="mt-4 text-blue-600">Procesando...</p>}
          </div>
          
          {detectionResult && (
            <div className="mt-6 p-4 bg-slate-50 rounded-lg">
              <h3 className="font-bold text-slate-800">Resultado de Detección:</h3>
              <p className="text-slate-700"><strong>Empleados:</strong> {detectionResult.empleados_detectados}</p>
              <p className="text-slate-700"><strong>Faltas EPP:</strong> {detectionResult.faltas_detectadas}</p>
              <p className="text-slate-700"><strong>Turno:</strong> {detectionResult.turno_actual}</p>
              <p className="text-slate-700"><strong>Descripción:</strong> {detectionResult.descripcion}</p>
            </div>
          )}
           {error && <div className="mt-4 text-center p-2 text-red-500">Error: {error}</div>}
        </div>
      </div>

      {/* --- Charts Section --- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Total de Faltas (Últimos 7 Días)</h2>
            <FoulsByDayChart data={dailyFouls} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Distribución de Faltas por Turno</h2>
            <FoulsByShiftPieChart data={stats?.estadisticas_por_turno} />
        </div>
      </div>

    </div>
  );
};

export default Home;