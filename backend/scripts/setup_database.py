#!/usr/bin/env python3
"""
Script para configurar la base de datos inicial con datos de prueba.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Evento, ConfiguracionDeteccion
from app.schemas import TurnoEnum
import random

def create_tables():
    """Crear todas las tablas."""
    print("Creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def insert_sample_data():
    """Insertar datos de ejemplo."""
    db = SessionLocal()
    
    try:
        print("Insertando datos de ejemplo...")
        
        # Configuraciones por defecto
        configs = [
            ConfiguracionDeteccion(
                nombre="confidence_threshold",
                valor="0.5",
                descripcion="Umbral de confianza para detección YOLO"
            ),
            ConfiguracionDeteccion(
                nombre="iou_threshold", 
                valor="0.45",
                descripcion="Umbral IoU para detección YOLO"
            ),
            ConfiguracionDeteccion(
                nombre="handrail_detection",
                valor="true",
                descripcion="Habilitar detección de barandales"
            ),
            ConfiguracionDeteccion(
                nombre="stair_detection",
                valor="true", 
                descripcion="Habilitar detección de escaleras"
            )
        ]
        
        for config in configs:
            existing = db.query(ConfiguracionDeteccion).filter(
                ConfiguracionDeteccion.nombre == config.nombre
            ).first()
            if not existing:
                db.add(config)
        
        # Eventos de ejemplo de los últimos 7 días
        base_date = datetime.now() - timedelta(days=7)
        
        for day in range(7):
            current_date = base_date + timedelta(days=day)
            
            for turno in TurnoEnum:
                # Generar 2-5 eventos por turno
                num_events = random.randint(2, 5)
                
                for _ in range(num_events):
                    empleados = random.randint(1, 8)
                    faltas = random.randint(0, min(empleados, 3))
                    confianza = random.randint(70, 95)
                    
                    # Calcular hora dentro del turno
                    if turno == TurnoEnum.TURNO_1:  # 6am-3pm
                        hour = random.randint(6, 14)
                    elif turno == TurnoEnum.TURNO_2:  # 3pm-10pm
                        hour = random.randint(15, 21)
                    else:  # 10pm-6am
                        hour = random.randint(22, 23) if random.choice([True, False]) else random.randint(0, 5)
                    
                    event_time = current_date.replace(
                        hour=hour,
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    
                    descripcion = f"Detección automática: {empleados} empleados, {faltas} faltas"
                    if faltas > 0:
                        descripcion += " - Empleados sin agarrar barandal detectados"
                    
                    evento = Evento(
                        fecha_hora=event_time,
                        empleados=empleados,
                        faltas=faltas,
                        turno=turno,
                        descripcion=descripcion,
                        confianza=confianza
                    )
                    
                    db.add(evento)
        
        db.commit()
        print("✅ Datos de ejemplo insertados exitosamente")
        
        # Mostrar estadísticas
        total_eventos = db.query(Evento).count()
        total_empleados = db.query(Evento.empleados).all()
        total_faltas = db.query(Evento.faltas).all()
        
        print(f"📊 Estadísticas:")
        print(f"   - Total eventos: {total_eventos}")
        print(f"   - Total empleados detectados: {sum(e[0] for e in total_empleados)}")
        print(f"   - Total faltas detectadas: {sum(f[0] for f in total_faltas)}")
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Función principal."""
    print("🔧 Configurando base de datos Employee Detection API")
    
    create_tables()
    insert_sample_data()
    
    print("🎉 Configuración completada exitosamente!")
    print("💡 Puedes iniciar la API con: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
