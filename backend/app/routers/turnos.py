from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel, Field, validator
from datetime import time

from app.database import get_db
from app.models import ConfiguracionDeteccion
from app.utils import get_turnos_config # Importar desde la nueva ubicación

router = APIRouter()

# ==================== SCHEMAS ====================

class TurnoHorario(BaseModel):
    inicio: time = Field(..., description="Hora de inicio del turno")
    fin: time = Field(..., description="Hora de fin del turno")

class TurnosUpdate(BaseModel):
    turno_1: TurnoHorario
    turno_2: TurnoHorario
    turno_3: TurnoHorario

    @validator('*', pre=True)
    def parse_time(cls, v):
        if isinstance(v, str):
            return time.fromisoformat(v)
        if isinstance(v, dict):
            return TurnoHorario(**v)
        return v

# ==================== ENDPOINTS ====================

@router.get("/", response_model=TurnosUpdate)
async def obtener_horarios_turnos(db: Session = Depends(get_db)):
    """
    Obtiene la configuración actual de los horarios de todos los turnos.
    """
    turnos_data = get_turnos_config(db)
    return TurnosUpdate(**turnos_data)

@router.put("/", response_model=TurnosUpdate)
async def actualizar_horarios_turnos(
    turnos_data: TurnosUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la configuración de horarios para todos los turnos.
    """
    for i in range(1, 4):
        turno_key = f"turno_{i}"
        horario = getattr(turnos_data, turno_key)
        
        # Upsert para la hora de inicio
        inicio_config = db.query(ConfiguracionDeteccion).filter(ConfiguracionDeteccion.nombre == f"{turno_key}_inicio").first()
        if inicio_config:
            inicio_config.valor = horario.inicio.isoformat()
        else:
            inicio_config = ConfiguracionDeteccion(
                nombre=f"{turno_key}_inicio",
                valor=horario.inicio.isoformat(),
                descripcion=f"Hora de inicio del turno {i}"
            )
            db.add(inicio_config)

        # Upsert para la hora de fin
        fin_config = db.query(ConfiguracionDeteccion).filter(ConfiguracionDeteccion.nombre == f"{turno_key}_fin").first()
        if fin_config:
            fin_config.valor = horario.fin.isoformat()
        else:
            fin_config = ConfiguracionDeteccion(
                nombre=f"{turno_key}_fin",
                valor=horario.fin.isoformat(),
                descripcion=f"Hora de fin del turno {i}"
            )
            db.add(fin_config)
            
    db.commit()
    
    # Devolver la configuración actualizada
    updated_turnos = get_turnos_config(db)
    return TurnosUpdate(**updated_turnos)
