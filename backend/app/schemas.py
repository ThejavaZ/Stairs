from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from enum import IntEnum

class TurnoEnum(IntEnum):
    TURNO_1 = 1  # 6am-3pm
    TURNO_2 = 2  # 3pm-10pm
    TURNO_3 = 3  # 10pm-6am

class EventoBase(BaseModel):
    empleados: int = Field(ge=0, description="Número de empleados detectados")
    faltas: int = Field(ge=0, description="Número de faltas detectadas")
    turno: TurnoEnum = Field(description="Turno de trabajo (1, 2, o 3)")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción del evento detectado")
    confianza: Optional[int] = Field(None, ge=0, le=100, description="Nivel de confianza de la detección (0-100)")
    camera_id: Optional[int] = Field(None, description="ID de la cámara asociada")

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id_evento: int
    fecha_hora: datetime
    
    class Config:
        from_attributes = True

class ReporteTurno(BaseModel):
    turno: TurnoEnum
    nombre_turno: str
    horario: str
    total_empleados: int
    total_faltas: int
    promedio_confianza: Optional[float] = None
    eventos: List[EventoResponse]
    fecha_inicio: datetime
    fecha_fin: datetime

class ReporteDiario(BaseModel):
    fecha: str
    total_empleados: int
    total_faltas: int
    promedio_confianza_general: Optional[float] = None
    turnos: List[ReporteTurno]
    resumen_por_turno: dict
    
class DetectionResult(BaseModel):
    empleados_detectados: int = Field(ge=0)
    faltas_detectadas: int = Field(ge=0)
    descripcion: str
    confianza: int = Field(ge=0, le=100)
    turno_actual: TurnoEnum
    timestamp: datetime
    image_base64: Optional[str] = None

class ConfiguracionBase(BaseModel):
    nombre: str = Field(max_length=100)
    valor: str = Field(max_length=500)
    descripcion: Optional[str] = None

class ConfiguracionCreate(ConfiguracionBase):
    pass

class ConfiguracionResponse(ConfiguracionBase):
    id: int
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True

class FormatoExporte(BaseModel):
    formato: str = Field(pattern="^(json|pdf|excel|word|xml)$")
    incluir_graficos: bool = False
    filtro_turno: Optional[TurnoEnum] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None

# Schemas for Camera Coordinates
class Coordinate(BaseModel):
    x: int
    y: int

class Rectangle(BaseModel):
    top_left: Coordinate
    bottom_right: Coordinate

class CameraCoordinates(BaseModel):
    handrail_left: Optional[Rectangle] = None
    handrail_right: Optional[Rectangle] = None
    stairs: Optional[Rectangle] = None

# Schemas for Camera
class CameraBase(BaseModel):
    name: str = Field(..., max_length=100, description="Unique name for the camera")
    ip_address: str = Field(..., max_length=100, description="IP address of the camera")
    port: int = Field(..., description="Port of the camera")
    username: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class CameraCreate(CameraBase):
    password: Optional[str] = Field(None, max_length=100)

class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=100)
    port: Optional[int] = Field(None, description="Port of the camera")
    username: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    handrail_coordinates: Optional[Dict[str, Any]] = None
    stairs_coordinates: Optional[Dict[str, Any]] = None

class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    handrail_coordinates: Optional[Dict[str, Any]] = None
    stairs_coordinates: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True