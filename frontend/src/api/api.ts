
const API_BASE_URL = 'http://localhost:8000/api';

// Función genérica para hacer fetch
const apiFetch = async (url: string, options: RequestInit = {}) => {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Accept': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Error fetching data' }));
    throw new Error(errorData.detail || 'Something went wrong');
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  return response.blob(); // Para reportes
};

// ==================== API Endpoints ====================

// Statistics
export const getStatisticsSummary = (days: number = 7) => {
  return apiFetch(`${API_BASE_URL}/estadisticas/resumen?dias=${days}`);
};

// Events
export const listEvents = (limit: number = 10, skip: number = 0, startDate?: string, endDate?: string) => {
  const params = new URLSearchParams({
    limit: String(limit),
    skip: String(skip),
  });
  if (startDate) params.append('fecha_inicio', startDate);
  if (endDate) params.append('fecha_fin', endDate);

  return apiFetch(`${API_BASE_URL}/eventos?${params.toString()}`);
};

export const deleteEvent = (eventId: number) => {
  return apiFetch(`${API_BASE_URL}/eventos/${eventId}`, { method: 'DELETE' });
};

// Detections
export const detectFromImage = (file: File, cameraId?: number) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const params = new URLSearchParams({ guardar_evento: 'true' });
  if (cameraId) {
    params.append('camera_id', String(cameraId));
  }

  return apiFetch(`${API_BASE_URL}/detect?${params.toString()}`, {
    method: 'POST',
    body: formData,
  });
};


// Cameras
export const getCameras = () => {
  return apiFetch(`${API_BASE_URL}/cameras/`);
};

export const getCamera = (cameraId: number) => {
  return apiFetch(`${API_BASE_URL}/cameras/${cameraId}`);
};

export const createCamera = (cameraData: any) => {
  return apiFetch(`${API_BASE_URL}/cameras/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cameraData),
  });
};

export const updateCamera = (cameraId: number, cameraData: any) => {
  return apiFetch(`${API_BASE_URL}/cameras/${cameraId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cameraData),
  });
};

export const deleteCamera = (cameraId: number) => {
  return apiFetch(`${API_BASE_URL}/cameras/${cameraId}`, { method: 'DELETE' });
};

export const detectFromCamera = (id: number) => {
    return apiFetch(`${API_BASE_URL}/cameras/${id}/detect`, { method: 'POST' });
};

export const updateCameraCoordinates = (id: number, coordinates: any) => {
  return apiFetch(`${API_BASE_URL}/cameras/${id}/coordinates`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(coordinates),
  });
};

// Reports
export const getReportPreview = (startDate: string, endDate: string, cameraId?: number) => {
  const params = new URLSearchParams({
    fecha_inicio: startDate,
    fecha_fin: endDate,
  });
  if (cameraId) {
    params.append('camera_id', String(cameraId));
  }
  return apiFetch(`${API_BASE_URL}/reportes/preview?${params.toString()}`);
};

export const downloadReport = (format: 'pdf' | 'excel' | 'word', startDate: string, endDate: string, cameraId?: number) => {
  const params = new URLSearchParams({
    fecha_inicio: startDate,
    fecha_fin: endDate,
  });
  if (cameraId) {
    params.append('camera_id', String(cameraId));
  }
  return apiFetch(`${API_BASE_URL}/reportes/${format}?${params.toString()}`);
};

// Settings
export const getSettings = () => {
  return apiFetch(`${API_BASE_URL}/configuracion/`);
};

export const updateSetting = (name: string, value: string) => {
  return apiFetch(`${API_BASE_URL}/configuracion/${name}?valor=${encodeURIComponent(value)}`, { 
    method: 'PUT' 
  });
};

// Turnos (Shifts)
export const getTurnos = () => {
  return apiFetch(`${API_BASE_URL}/turnos/`);
};

export const updateTurnos = (turnosData: any) => {
  return apiFetch(`${API_BASE_URL}/turnos/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(turnosData),
  });
};
