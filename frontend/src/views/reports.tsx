import { useState, useEffect, ChangeEvent } from 'react';
import { getReportPreview, downloadReport, getCameras } from '../api/api';
import { Calendar, Users, AlertTriangle, FileText, FileSpreadsheet, FileType, Video } from 'lucide-react';

// Helper to format date to YYYY-MM-DD
const toISODateString = (date: Date) => {
  return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().split('T')[0];
};

const ReportCard = ({ turno }: { turno: any }) => (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <h3 className="text-xl font-bold text-slate-800">{turno.nombre_turno}</h3>
        <p className="text-sm text-slate-500 mb-4">{turno.horario}</p>
        <div className="flex justify-around text-center">
            <div>
                <p className="text-2xl font-bold text-slate-800">{turno.total_empleados}</p>
                <p className="text-sm text-slate-600">Empleados</p>
            </div>
            <div>
                <p className="text-2xl font-bold text-slate-800">{turno.total_faltas}</p>
                <p className="text-sm text-slate-600">Faltas</p>
            </div>
        </div>
        <p className="text-xs text-center mt-4 text-slate-400">{turno.eventos.length} eventos registrados</p>
    </div>
);

const Reports = () => {
  const [startDate, setStartDate] = useState(toISODateString(new Date()));
  const [endDate, setEndDate] = useState(toISODateString(new Date()));
  const [cameras, setCameras] = useState<any[]>([]);
  const [selectedCamera, setSelectedCamera] = useState(''); // Empty string for 'All'
  
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState<string | null>(null); // pdf, excel, word

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const camerasData = await getCameras();
        setCameras(camerasData);
      } catch (err: any) {
        console.error("Failed to fetch cameras:", err);
      }
    };
    fetchCameras();
  }, []);

  useEffect(() => {
    const fetchReport = async () => {
      if (!startDate || !endDate) return;
      setLoading(true);
      setError('');
      setReport(null);
      try {
        const data = await getReportPreview(startDate, endDate, selectedCamera ? Number(selectedCamera) : undefined);
        setReport(data);
      } catch (err: any) {
        setError('No se encontraron datos para los filtros seleccionados.');
        console.error(err);
      }
      setLoading(false);
    };
    fetchReport();
  }, [startDate, endDate, selectedCamera]);

  const handleDownload = async (format: 'pdf' | 'excel' | 'word') => {
    if (!startDate || !endDate) return;
    setDownloading(format);
    try {
        const blob = await downloadReport(format, startDate, endDate, selectedCamera ? Number(selectedCamera) : undefined);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_${startDate}_a_${endDate}.${{pdf: 'pdf', excel: 'xlsx', word: 'docx'}[format]}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err: any) {
        alert(`Error al descargar el reporte: ${err.message}`);
    } finally {
        setDownloading(null);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-4 md:mb-0">Generador de Reportes</h1>
        <div className="flex flex-wrap gap-4">
            <div className="flex items-center bg-white p-2 border border-slate-200 rounded-lg shadow-sm">
                <Calendar className="mr-2 text-slate-500" />
                <input type="date" value={startDate} onChange={(e: ChangeEvent<HTMLInputElement>) => setStartDate(e.target.value)} className="bg-transparent focus:outline-none text-slate-700"/>
            </div>
            <div className="flex items-center bg-white p-2 border border-slate-200 rounded-lg shadow-sm">
                <Calendar className="mr-2 text-slate-500" />
                <input type="date" value={endDate} onChange={(e: ChangeEvent<HTMLInputElement>) => setEndDate(e.target.value)} className="bg-transparent focus:outline-none text-slate-700"/>
            </div>
            <div className="flex items-center bg-white p-2 border border-slate-200 rounded-lg shadow-sm">
                <Video className="mr-2 text-slate-500" />
                <select value={selectedCamera} onChange={(e: ChangeEvent<HTMLSelectElement>) => setSelectedCamera(e.target.value)} className="bg-transparent focus:outline-none text-slate-700">
                    <option value="">Todas las Cámaras</option>
                    {cameras.map(cam => (
                        <option key={cam.id} value={cam.id}>{cam.name}</option>
                    ))}
                </select>
            </div>
        </div>
      </div>

      {loading && <div className="text-center p-8 text-slate-500">Generando reporte...</div>}
      {error && !loading && <div className="text-center p-8 text-slate-500">{error}</div>}

      {report && !loading && (
        <div className="space-y-8">
          {/* Summary Section */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Resumen del Periodo: {report.fecha}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-center">
                <div className="bg-slate-50 p-6 rounded-lg">
                    <Users className="mx-auto text-blue-500 mb-2" size={32}/>
                    <p className="text-4xl font-bold text-blue-800">{report.total_empleados}</p>
                    <p className="text-slate-600">Total Empleados</p>
                </div>
                <div className="bg-red-50 p-6 rounded-lg">
                    <AlertTriangle className="mx-auto text-red-500 mb-2" size={32}/>
                    <p className="text-4xl font-bold text-red-800">{report.total_faltas}</p>
                    <p className="text-slate-600">Total Faltas de EPP</p>
                </div>
            </div>
          </div>

          {/* Shifts Section */}
          <div>
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Desglose por Turno</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {report.turnos.map((turno: any) => <ReportCard key={turno.turno} turno={turno} />)}
            </div>
          </div>

          {/* Download Section */}
          <div>
            <h2 className="text-2xl font-bold text-slate-800 mb-4">Descargar Reporte Completo</h2>
            <div className="flex flex-wrap gap-4">
              <button onClick={() => handleDownload('pdf')} disabled={downloading === 'pdf'} className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-red-400 shadow-sm">
                <FileText className="mr-2"/> {downloading === 'pdf' ? 'Generando...' : 'PDF'}
              </button>
              <button onClick={() => handleDownload('excel')} disabled={downloading === 'excel'} className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-green-400 shadow-sm">
                <FileSpreadsheet className="mr-2"/> {downloading === 'excel' ? 'Generando...' : 'Excel'}
              </button>
              <button onClick={() => handleDownload('word')} disabled={downloading === 'word'} className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 shadow-sm">
                <FileType className="mr-2"/> {downloading === 'word' ? 'Generando...' : 'Word'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;