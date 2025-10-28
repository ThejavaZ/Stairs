from datetime import datetime, time, timedelta
from typing import Tuple, Dict
from sqlalchemy.orm import Session

from app.schemas import TurnoEnum
from app.models import ConfiguracionDeteccion

# Cache para la configuración de turnos para no consultar la BD en cada llamada
_turnos_config_cache = {}

def get_turnos_config(db: Session) -> Dict[str, Dict[str, time]]:
    """Obtiene la configuración de horarios de turnos desde la BD, con cache."""
    # Esta función se llama múltiples veces en un request, el cache ayuda
    if _turnos_config_cache:
        return _turnos_config_cache

    config_keys = [
        "turno_1_inicio", "turno_1_fin",
        "turno_2_inicio", "turno_2_fin",
        "turno_3_inicio", "turno_3_fin"
    ]
    
    configs = db.query(ConfiguracionDeteccion).filter(
        ConfiguracionDeteccion.nombre.in_(config_keys)
    ).all()
    
    config_dict = {c.nombre: c.valor for c in configs}

    defaults = {
        "turno_1_inicio": "06:00:00", "turno_1_fin": "15:00:00",
        "turno_2_inicio": "15:00:00", "turno_2_fin": "22:00:00",
        "turno_3_inicio": "22:00:00", "turno_3_fin": "06:00:00"
    }

    config = {
        "turno_1": {
            "inicio": time.fromisoformat(config_dict.get("turno_1_inicio", defaults["turno_1_inicio"])),
            "fin": time.fromisoformat(config_dict.get("turno_1_fin", defaults["turno_1_fin"]))
        },
        "turno_2": {
            "inicio": time.fromisoformat(config_dict.get("turno_2_inicio", defaults["turno_2_inicio"])),
            "fin": time.fromisoformat(config_dict.get("turno_2_fin", defaults["turno_2_fin"]))
        },
        "turno_3": {
            "inicio": time.fromisoformat(config_dict.get("turno_3_inicio", defaults["turno_3_inicio"])),
            "fin": time.fromisoformat(config_dict.get("turno_3_fin", defaults["turno_3_fin"]))
        }
    }
    _turnos_config_cache.update(config)
    return config

def obtener_horarios_turno(db: Session, turno: TurnoEnum) -> Tuple[time, time]:
    """Retorna los horarios de inicio y fin para un turno específico desde la BD."""
    turnos_config = get_turnos_config(db)
    horarios = turnos_config[f"turno_{turno.value}"]
    return horarios['inicio'], horarios['fin']

def obtener_turno_actual(db: Session) -> TurnoEnum:
    """Determina el turno actual basado en la hora del sistema y la config de la BD."""
    hora_actual = datetime.now().time()
    turnos_config = get_turnos_config(db)

    t1_inicio = turnos_config['turno_1']['inicio']
    t1_fin = turnos_config['turno_1']['fin']
    t2_inicio = turnos_config['turno_2']['inicio']
    t2_fin = turnos_config['turno_2']['fin']

    if t1_inicio <= hora_actual < t1_fin:
        return TurnoEnum.TURNO_1
    elif t2_inicio <= hora_actual < t2_fin:
        return TurnoEnum.TURNO_2
    else:
        # El turno 3 puede cruzar la medianoche
        return TurnoEnum.TURNO_3

def obtener_nombre_turno(turno: TurnoEnum) -> str:
    """Retorna el nombre descriptivo del turno."""
    nombres = {
        TurnoEnum.TURNO_1: "Turno Mañana",
        TurnoEnum.TURNO_2: "Turno Tarde", 
        TurnoEnum.TURNO_3: "Turno Noche"
    }
    return nombres[turno]

def obtener_horario_turno_str(db: Session, turno: TurnoEnum) -> str:
    """Retorna el horario del turno como string legible desde la BD."""
    inicio, fin = obtener_horarios_turno(db, turno)
    return f"{inicio.strftime('%I:%M %p')} - {fin.strftime('%I:%M %p')}"

def calcular_rango_fecha_turno(db: Session, fecha: datetime, turno: TurnoEnum) -> Tuple[datetime, datetime]:
    """Calcula el rango de fechas para un turno específico en una fecha dada desde la BD."""
    inicio_hora, fin_hora = obtener_horarios_turno(db, turno)
    
    fecha_inicio = datetime.combine(fecha.date(), inicio_hora)
    
    # Si el turno cruza la medianoche (ej. 22:00 - 06:00)
    if fin_hora < inicio_hora:
        fecha_fin = datetime.combine(fecha.date() + timedelta(days=1), fin_hora)
    else:
        fecha_fin = datetime.combine(fecha.date(), fin_hora)
    
    return fecha_inicio, fecha_fin

def validar_deteccion(empleados: int, faltas: int) -> bool:
    """Valida que los datos de detección sean coherentes."""
    if empleados < 0 or faltas < 0:
        return False
    if faltas > empleados:
        return False
    return True
