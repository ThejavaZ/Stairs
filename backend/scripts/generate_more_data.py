#!/usr/bin/env python3
"""
Script para generar más datos de prueba para la base de datos.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Evento, Camera
from app.schemas import TurnoEnum
import random

def create_tables():
    """Crear todas las tablas si no existen."""
    print("Verificando y creando tablas si es necesario...")
    Base.metadata.create_all(bind=engine)
    print("Tablas listas.")

def setup_cameras():
    """Asegura que haya cámaras en la base de datos."""
    db = SessionLocal()
    try:
        if db.query(Camera).count() == 0:
            print("No se encontraron cámaras. Insertando 3 cámaras de ejemplo...")
            cameras = [
                Camera(id=1, name="Cámara Escalera Principal", ip_address="192.168.1.101", is_active=True),
                Camera(id=2, name="Cámara Pasillo Norte", ip_address="192.168.1.102", is_active=True),
                Camera(id=3, name="Cámara Entrada Sur", ip_address="192.168.1.103", is_active=False),
            ]
            db.add_all(cameras)
            db.commit()
            print("3 camaras de ejemplo insertadas.")
        else:
            print("DB con cámaras existentes.")
    finally:
        db.close()

def insert_more_data():
    """Insertar más datos de ejemplo."""
    db = SessionLocal()
    
    try:
        print("Insertando 15 registros de eventos adicionales...")
        
        num_cameras = db.query(Camera).count()
        camera_ids = [c.id for c in db.query(Camera).all()] if num_cameras > 0 else []

        base_date = datetime.now()
        
        for i in range(15):
            turno = random.choice(list(TurnoEnum))
            
            empleados = random.randint(1, 10)
            faltas = random.randint(0, min(empleados, 4)) # Max 4 faltas por evento
            confianza = random.randint(60, 99)
            
            event_time = base_date - timedelta(days=random.randint(0, 2), 
                                               hours=random.randint(0, 23), 
                                               minutes=random.randint(0, 59))

            descripcion = f"Detección automática adicional: {empleados} empleados, {faltas} faltas"
            if faltas > 0:
                descripcion += " - Empleados sin agarrar barandal detectados"
            
            evento = Evento(
                fecha_hora=event_time,
                empleados=empleados,
                faltas=faltas,
                turno=turno.value,
                descripcion=descripcion,
                confianza=confianza,
                camera_id=random.choice(camera_ids) if camera_ids else None
            )
            
            db.add(evento)
        
        db.commit()
        print(f"15 registros de eventos adicionales insertados exitosamente.")
        
    except Exception as e:
        print(f"Error insertando datos adicionales: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    setup_cameras()
    insert_more_data()
