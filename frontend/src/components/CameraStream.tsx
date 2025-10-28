import { useState, MouseEvent, useEffect } from 'react';
import { Settings } from 'lucide-react';
import { updateCameraCoordinates, getCamera } from '../api/api';

interface CameraStreamProps {
  cameraId: number;
}

const CameraStream: React.FC<CameraStreamProps> = ({ cameraId }) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [handrailLeft, setHandrailLeft] = useState({ x: 50, y: 100, width: 50, height: 300 });
  const [handrailRight, setHandrailRight] = useState({ x: 700, y: 100, width: 50, height: 300 });
  const [stairs, setStairs] = useState({ x: 100, y: 100, width: 600, height: 300 });

  const [drawing, setDrawing] = useState(false);
  const [rectType, setRectType] = useState('');
  const [startPoint, setStartPoint] = useState({ x: 0, y: 0 });

  const [editHandrailLeft, setEditHandrailLeft] = useState(false);
  const [editHandrailRight, setEditHandrailRight] = useState(false);
  const [editStairs, setEditStairs] = useState(false);

  const streamUrl = `/api/cameras/${cameraId}/stream`;

  // Load initial coordinates when settings open
  useEffect(() => {
    const fetchCameraDetails = async () => {
      try {
        const cameraDetails = await getCamera(cameraId);
        if (cameraDetails.handrail_coordinates) {
          setHandrailLeft({
            x: cameraDetails.handrail_coordinates.left.top_left.x,
            y: cameraDetails.handrail_coordinates.left.top_left.y,
            width: cameraDetails.handrail_coordinates.left.bottom_right.x - cameraDetails.handrail_coordinates.left.top_left.x,
            height: cameraDetails.handrail_coordinates.left.bottom_right.y - cameraDetails.handrail_coordinates.left.top_left.y,
          });
          setHandrailRight({
            x: cameraDetails.handrail_coordinates.right.top_left.x,
            y: cameraDetails.handrail_coordinates.right.top_left.y,
            width: cameraDetails.handrail_coordinates.right.bottom_right.x - cameraDetails.handrail_coordinates.right.top_left.x,
            height: cameraDetails.handrail_coordinates.right.bottom_right.y - cameraDetails.handrail_coordinates.right.top_left.y,
          });
        }
        if (cameraDetails.stairs_coordinates) {
          setStairs({
            x: cameraDetails.stairs_coordinates.top_left.x,
            y: cameraDetails.stairs_coordinates.top_left.y,
            width: cameraDetails.stairs_coordinates.bottom_right.x - cameraDetails.stairs_coordinates.top_left.x,
            height: cameraDetails.stairs_coordinates.bottom_right.y - cameraDetails.stairs_coordinates.top_left.y,
          });
        }
      } catch (error) {
        console.error("Error loading camera coordinates:", error);
      }
    };

    if (isSettingsOpen) {
      fetchCameraDetails();
    }
  }, [isSettingsOpen, cameraId]);

  const handleSave = async () => {
    const coordinates = {
      handrail_left: { top_left: { x: handrailLeft.x, y: handrailLeft.y }, bottom_right: { x: handrailLeft.x + handrailLeft.width, y: handrailLeft.y + handrailLeft.height } },
      handrail_right: { top_left: { x: handrailRight.x, y: handrailRight.y }, bottom_right: { x: handrailRight.x + handrailRight.width, y: handrailRight.y + handrailRight.height } },
      stairs: { top_left: { x: stairs.x, y: stairs.y }, bottom_right: { x: stairs.x + stairs.width, y: stairs.y + stairs.height } },
    };
    try {
      await updateCameraCoordinates(cameraId, coordinates);
      setIsSettingsOpen(false);
    } catch (error) {
      alert('Error al guardar las coordenadas');
    }
  };

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    if (!editHandrailLeft && !editHandrailRight && !editStairs) return;

    setDrawing(true);
    const rect = e.currentTarget.getBoundingClientRect();
    setStartPoint({ x: e.clientX - rect.left, y: e.clientY - rect.top });

    if (editHandrailLeft) setRectType('handrailLeft');
    else if (editHandrailRight) setRectType('handrailRight');
    else if (editStairs) setRectType('stairs');
  };

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!drawing) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const endPoint = { x: e.clientX - rect.left, y: e.clientY - rect.top };
    const newRect = {
        x: Math.min(startPoint.x, endPoint.x),
        y: Math.min(startPoint.y, endPoint.y),
        width: Math.abs(startPoint.x - endPoint.x),
        height: Math.abs(startPoint.y - endPoint.y),
    };
    if (rectType === 'handrailLeft') {
        setHandrailLeft(newRect);
    } else if (rectType === 'handrailRight') {
        setHandrailRight(newRect);
    } else if (rectType === 'stairs') {
        setStairs(newRect);
    }
  };

  const handleMouseUp = () => {
    setDrawing(false);
    setRectType('');
  };

  const getBorderStyle = (type: string) => {
    let style = { position: 'absolute' as 'absolute', border: '2px dashed', cursor: 'grab' };
    if (type === 'handrailLeft' && editHandrailLeft) style.border = '2px dashed yellow';
    if (type === 'handrailRight' && editHandrailRight) style.border = '2px dashed yellow';
    if (type === 'stairs' && editStairs) style.border = '2px dashed yellow';
    return style;
  };

  return (
    <div className="relative w-full bg-black rounded-lg overflow-hidden shadow-lg">
      <img src={streamUrl} alt={`Cámara ${cameraId}`} className="w-full h-auto" />
      <div className="absolute top-2 right-2">
        <button 
          onClick={() => setIsSettingsOpen(true)} 
          className="p-2 bg-black bg-opacity-50 rounded-full text-white hover:bg-opacity-75 transition-all duration-200"
        >
          <Settings size={20} />
        </button>
      </div>

      {isSettingsOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
          <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-4xl">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">Configurar Zonas de Detección</h2>
            
            <div className="flex flex-wrap gap-4 mb-4">
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={editHandrailLeft} onChange={() => setEditHandrailLeft(!editHandrailLeft)} className="form-checkbox" />
                    <span>Barandal Izquierdo</span>
                </label>
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={editHandrailRight} onChange={() => setEditHandrailRight(!editHandrailRight)} className="form-checkbox" />
                    <span>Barandal Derecho</span>
                </label>
                <label className="flex items-center space-x-2">
                    <input type="checkbox" checked={editStairs} onChange={() => setEditStairs(!editStairs)} className="form-checkbox" />
                    <span>Escaleras</span>
                </label>
            </div>

            <div 
                className="relative w-full aspect-video bg-gray-200 rounded-lg overflow-hidden"
                onMouseDown={handleMouseDown} 
                onMouseMove={handleMouseMove} 
                onMouseUp={handleMouseUp}
            >
              <img src={streamUrl} alt={`Configuración de Cámara ${cameraId}`} className="w-full h-full" />
              <div 
                style={{ ...getBorderStyle('handrailLeft'), left: handrailLeft.x, top: handrailLeft.y, width: handrailLeft.width, height: handrailLeft.height, borderColor: editHandrailLeft ? 'yellow' : 'blue' }}
                className="bg-blue-500 bg-opacity-25"
              />
              <div 
                style={{ ...getBorderStyle('handrailRight'), left: handrailRight.x, top: handrailRight.y, width: handrailRight.width, height: handrailRight.height, borderColor: editHandrailRight ? 'yellow' : 'blue' }}
                className="bg-blue-500 bg-opacity-25"
              />
              <div 
                style={{ ...getBorderStyle('stairs'), left: stairs.x, top: stairs.y, width: stairs.width, height: stairs.height, borderColor: editStairs ? 'yellow' : 'green' }}
                className="bg-green-500 bg-opacity-25"
              />
            </div>
            <div className="flex justify-end space-x-4 pt-4">
              <button type="button" onClick={() => setIsSettingsOpen(false)} className="px-4 py-2 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300">Cancelar</button>
              <button type="button" onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CameraStream;
