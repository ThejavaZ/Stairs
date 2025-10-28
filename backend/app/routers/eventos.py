from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, timedelta, time
import io
import cv2
import numpy as np

from app.database import get_db
from app.models import Evento, Camera
from app.schemas import (
    EventoCreate, EventoResponse, ReporteTurno, ReporteDiario, 
    DetectionResult, TurnoEnum
)
from app.utils import (
    obtener_turno_actual, obtener_nombre_turno, obtener_horario_turno_str,
    calcular_rango_fecha_turno, validar_deteccion
)
from app.services.vision import detection_service
from app.services.reports import report_generator

router = APIRouter()

# ==================== ENDPOINTS DE EVENTOS ====================

@router.get("/eventos", response_model=List[EventoResponse])
async def listar_eventos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    turno: Optional[TurnoEnum] = Query(None, description="Filtrar por turno específico"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio para filtrar"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin para filtrar"),
    camera_id: Optional[int] = Query(None, description="Filtrar por ID de cámara"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos con filtros opcionales.
    """
    query = db.query(Evento)
    
    if turno is not None:
        query = query.filter(Evento.turno == turno)
    if fecha_inicio:
        query = query.filter(Evento.fecha_hora >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Evento.fecha_hora <= fecha_fin)
    if camera_id is not None:
        query = query.filter(Evento.camera_id == camera_id)
    
    query = query.order_by(Evento.fecha_hora.desc())
    
    eventos = query.offset(skip).limit(limit).all()
    return eventos

@router.post("/eventos", response_model=EventoResponse)
async def crear_evento(
    evento: EventoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo evento manualmente.
    """
    if not validar_deteccion(evento.empleados, evento.faltas):
        raise HTTPException(
            status_code=400,
            detail="Datos de detección inválidos: las faltas no pueden ser mayores que los empleados"
        )
    
    db_evento = Evento(**evento.dict())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.delete("/eventos/{evento_id}", status_code=204)
async def eliminar_evento(
    evento_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un evento específico.
    """
    evento = db.query(Evento).filter(Evento.id_evento == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db.delete(evento)
    db.commit()
    return Response(status_code=204)

# ==================== ENDPOINTS DE DETECCIÓN ====================

@router.post("/detect", response_model=DetectionResult)
async def detectar_empleados_imagen(
    file: UploadFile = File(..., description="Imagen para procesar"),
    camera_id: Optional[int] = Query(None, description="ID de la cámara de origen"),
    guardar_evento: bool = Query(True, description="Guardar resultado como evento en BD"),
    db: Session = Depends(get_db)
):
    """
    Procesa una imagen para detectar empleados y faltas.
    """
    if camera_id:
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(status_code=404, detail=f"Cámara con id {camera_id} no encontrada")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")
        
        result = detection_service.process_image(db, image)
        
        if guardar_evento and (result.empleados_detectados > 0 or result.faltas_detectadas > 0):
            db_evento = Evento(
                empleados=result.empleados_detectados,
                faltas=result.faltas_detectadas,
                turno=result.turno_actual,
                descripcion=result.descripcion,
                confianza=result.confianza,
                camera_id=camera_id
            )
            db.add(db_evento)
            db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

# ==================== ENDPOINTS DE GENERACIÓN DE REPORTES ====================

@router.get("/reportes/preview", response_model=ReporteDiario)
async def preview_reporte(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del rango del reporte (por defecto hoy)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del rango del reporte (por defecto hoy)"),
    camera_id: Optional[int] = Query(None, description="Filtrar por un ID de cámara específico"),
    db: Session = Depends(get_db)
):
    """
    Genera una vista previa del reporte en formato JSON para un rango de fechas y cámara opcional.
    """
    _fecha_inicio = fecha_inicio or date.today()
    _fecha_fin = fecha_fin or date.today()

    start_datetime = datetime.combine(_fecha_inicio, time.min)
    end_datetime = datetime.combine(_fecha_fin, time.max)

    query = db.query(Evento).filter(Evento.fecha_hora.between(start_datetime, end_datetime))
    if camera_id:
        query = query.filter(Evento.camera_id == camera_id)
    eventos_filtrados = query.order_by(Evento.fecha_hora.desc()).all()

    turnos_reportes = []
    total_empleados_dia = 0
    total_faltas_dia = 0
    todas_confianzas = []

    for turno in TurnoEnum:
        eventos_del_turno = [e for e in eventos_filtrados if e.turno == turno]
        total_empleados = sum(evento.empleados for evento in eventos_del_turno)
        total_faltas = sum(evento.faltas for evento in eventos_del_turno)
        confianzas = [evento.confianza for evento in eventos_del_turno if evento.confianza is not None]
        promedio_confianza = sum(confianzas) / len(confianzas) if confianzas else None
        _, fin_turno_meta = calcular_rango_fecha_turno(db, start_datetime, turno)

        reporte_turno = ReporteTurno(
            turno=turno, nombre_turno=obtener_nombre_turno(turno),
            horario=obtener_horario_turno_str(db, turno), total_empleados=total_empleados,
            total_faltas=total_faltas, promedio_confianza=promedio_confianza,
            eventos=eventos_del_turno, fecha_inicio=start_datetime, fecha_fin=fin_turno_meta
        )
        turnos_reportes.append(reporte_turno)
        total_empleados_dia += total_empleados
        total_faltas_dia += total_faltas
        todas_confianzas.extend(confianzas)

    promedio_confianza_general = sum(todas_confianzas) / len(todas_confianzas) if todas_confianzas else None

    return ReporteDiario(
        fecha=f"{_fecha_inicio.isoformat()} al {_fecha_fin.isoformat()}",
        total_empleados=total_empleados_dia, total_faltas=total_faltas_dia,
        promedio_confianza_general=promedio_confianza_general, turnos=turnos_reportes,
        resumen_por_turno={f"turno_{t.turno.value}": {"empleados": t.total_empleados, "faltas": t.total_faltas, "eventos": len(t.eventos)} for t in turnos_reportes}
    )

@router.get("/reportes/{formato}")
async def generar_reporte(
    formato: str,
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del rango del reporte (por defecto hoy)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del rango del reporte (por defecto hoy)"),
    camera_id: Optional[int] = Query(None, description="Filtrar por un ID de cámara específico"),
    incluir_graficos: bool = Query(True, description="Incluir gráficos en el reporte"),
    db: Session = Depends(get_db)
):
    """
    Genera un reporte en el formato especificado para un rango de fechas y una cámara opcional.
    """
    _fecha_inicio = fecha_inicio or date.today()
    _fecha_fin = fecha_fin or date.today()

    if formato.lower() not in ['pdf', 'word', 'excel', 'xml', 'json']:
        raise HTTPException(status_code=400, detail="Formato no soportado")

    start_datetime = datetime.combine(_fecha_inicio, time.min)
    end_datetime = datetime.combine(_fecha_fin, time.max)

    query = db.query(Evento).filter(Evento.fecha_hora.between(start_datetime, end_datetime))
    if camera_id:
        query = query.filter(Evento.camera_id == camera_id)
    eventos_filtrados = query.order_by(Evento.fecha_hora.desc()).all()

    turnos_reportes = []
    total_empleados_dia = 0
    total_faltas_dia = 0
    todas_confianzas = []

    for turno in TurnoEnum:
        eventos_del_turno = [e for e in eventos_filtrados if e.turno == turno]
        total_empleados = sum(evento.empleados for evento in eventos_del_turno)
        total_faltas = sum(evento.faltas for evento in eventos_del_turno)
        confianzas = [evento.confianza for evento in eventos_del_turno if evento.confianza is not None]
        promedio_confianza = sum(confianzas) / len(confianzas) if confianzas else None
        _, fin_turno_meta = calcular_rango_fecha_turno(db, start_datetime, turno)

        reporte_turno = ReporteTurno(
            turno=turno, nombre_turno=obtener_nombre_turno(turno),
            horario=obtener_horario_turno_str(db, turno), total_empleados=total_empleados,
            total_faltas=total_faltas, promedio_confianza=promedio_confianza,
            eventos=eventos_del_turno, fecha_inicio=start_datetime, fecha_fin=fin_turno_meta
        )
        turnos_reportes.append(reporte_turno)
        total_empleados_dia += total_empleados
        total_faltas_dia += total_faltas
        todas_confianzas.extend(confianzas)

    promedio_confianza_general = sum(todas_confianzas) / len(todas_confianzas) if todas_confianzas else None

    reporte_data = ReporteDiario(
        fecha=f"{_fecha_inicio.isoformat()} al {_fecha_fin.isoformat()}",
        total_empleados=total_empleados_dia, total_faltas=total_faltas_dia,
        promedio_confianza_general=promedio_confianza_general, turnos=turnos_reportes,
        resumen_por_turno={f"turno_{t.turno.value}": {"empleados": t.total_empleados, "faltas": t.total_faltas, "eventos": len(t.eventos)} for t in turnos_reportes}
    )

    try:
        content_map = {
            'pdf': (report_generator.generate_pdf_report(reporte_data, incluir_graficos), "application/pdf"),
            'word': (report_generator.generate_word_report(reporte_data, incluir_graficos), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            'excel': (report_generator.generate_excel_report(reporte_data, incluir_graficos), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            'xml': (report_generator.generate_xml_report(reporte_data).encode('utf-8'), "application/xml"),
            'json': (report_generator.generate_json_report(reporte_data).encode('utf-8'), "application/json")
        }
        content, media_type = content_map[formato.lower()]
        filename = f"reporte_{_fecha_inicio}_a_{_fecha_fin}.{formato.lower() if formato != 'word' else 'docx'}"
        
        return Response(content=content, media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")