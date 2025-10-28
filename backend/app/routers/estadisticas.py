from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Evento
from app.schemas import TurnoEnum

router = APIRouter()

@router.get("/resumen")
async def obtener_estadisticas_resumen(
    dias: int = Query(7, ge=1, le=365, description="Número de días hacia atrás"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas resumidas de los últimos N días.
    """
    fecha_inicio = datetime.now() - timedelta(days=dias)
    
    total_eventos = db.query(func.count(Evento.id_evento)).filter(
        Evento.fecha_hora >= fecha_inicio
    ).scalar()
    
    total_empleados = db.query(func.sum(Evento.empleados)).filter(
        Evento.fecha_hora >= fecha_inicio
    ).scalar() or 0
    
    total_faltas = db.query(func.sum(Evento.faltas)).filter(
        Evento.fecha_hora >= fecha_inicio
    ).scalar() or 0
    
    promedio_confianza = db.query(func.avg(Evento.confianza)).filter(
        and_(
            Evento.fecha_hora >= fecha_inicio,
            Evento.confianza.isnot(None)
        )
    ).scalar()
    
    stats_por_turno = {}
    for turno in TurnoEnum:
        turno_stats = db.query(
            func.count(Evento.id_evento).label('eventos'),
            func.sum(Evento.empleados).label('empleados'),
            func.sum(Evento.faltas).label('faltas')
        ).filter(
            and_(
                Evento.turno == turno,
                Evento.fecha_hora >= fecha_inicio
            )
        ).first()
        
        stats_por_turno[f"turno_{turno.value}"] = {
            "eventos": turno_stats.eventos or 0,
            "empleados": turno_stats.empleados or 0,
            "faltas": turno_stats.faltas or 0
        }
    
    return {
        "periodo_dias": dias,
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": datetime.now().isoformat(),
        "total_eventos": total_eventos,
        "total_empleados": total_empleados,
        "total_faltas": total_faltas,
        "promedio_confianza": round(promedio_confianza, 2) if promedio_confianza else None,
        "tasa_faltas": round((total_faltas / total_empleados * 100), 2) if total_empleados > 0 else 0,
        "estadisticas_por_turno": stats_por_turno
    }
