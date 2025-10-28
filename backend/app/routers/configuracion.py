from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import ConfiguracionDeteccion

router = APIRouter()

@router.get("/")
async def obtener_configuracion(db: Session = Depends(get_db)):
    """
    Obtiene la configuración actual del sistema.
    """
    configuraciones = db.query(ConfiguracionDeteccion).all()
    
    config_dict = {config.nombre: config.valor for config in configuraciones}
    
    # Valores por defecto si no existen
    defaults = {
        "confidence_threshold": "0.5",
        "iou_threshold": "0.45",
        "handrail_detection": "true",
        "stair_detection": "true"
    }
    
    for key, default_value in defaults.items():
        if key not in config_dict:
            config_dict[key] = default_value
    
    return config_dict

@router.put("/{nombre}")
async def actualizar_configuracion(
    nombre: str,
    valor: str,
    descripcion: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Actualiza una configuración específica.
    """
    config = db.query(ConfiguracionDeteccion).filter(
        ConfiguracionDeteccion.nombre == nombre
    ).first()
    
    if config:
        config.valor = valor
        if descripcion:
            config.descripcion = descripcion
    else:
        config = ConfiguracionDeteccion(
            nombre=nombre,
            valor=valor,
            descripcion=descripcion
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    
    return {"message": f"Configuración '{nombre}' actualizada", "config": config}
