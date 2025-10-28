from sqlalchemy import Column, Integer, DateTime, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Evento(Base):
    __tablename__ = "eventos"
    
    id_evento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())
    empleados = Column(Integer, default=0)
    faltas = Column(Integer, default=0)
    turno = Column(Integer)  # 1: 6am-3pm, 2: 3pm-10pm, 3: 10pm-6am
    descripcion = Column(Text, nullable=True)
    confianza = Column(Integer, default=0)  # 0-100 confidence percentage
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True) # Puede ser nulo para eventos manuales
    
    camera = relationship("Camera", back_populates="eventos")
    
    def __repr__(self):
        return f"<Evento(id={self.id_evento}, empleados={self.empleados}, faltas={self.faltas}, turno={self.turno})>"

class ConfiguracionDeteccion(Base):
    __tablename__ = "configuracion_deteccion"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), unique=True, index=True)
    valor = Column(String(500))
    descripcion = Column(Text, nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfiguracionDeteccion(nombre={self.nombre}, valor={self.valor})>"

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    ip_address = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False, default=554)
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Coordenadas para los barandales y escaleras (JSON)
    # Ejemplo barandales: {"left": {"x1": 1, "y1": 1, "x2": 1, "y2": 1}, "right": {"x1": 1, "y1": 1, "x2": 1, "y2": 1}}
    # Ejemplo escaleras: {"x1": 1, "y1": 1, "x2": 1, "y2": 1}
    handrail_coordinates = Column(JSON, nullable=True)
    stairs_coordinates = Column(JSON, nullable=True)

    eventos = relationship("Evento", back_populates="camera")

    def __repr__(self):
        return f"<Camera(id={self.id}, name='{self.name}', ip='{self.ip_address}')>"