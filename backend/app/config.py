import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno.
    """
    
    # Configuración de la aplicación
    app_name: str = "Employee Detection API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Configuración de base de datos
    database_url: str = "sqlite:///./employee_detection.db"
    
    # Configuración de CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # Configuración de detección
    yolo_model_path: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    
    # Configuración de cámara
    camera_id: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    
    # Configuración de reportes
    reports_dir: str = "./reports"
    max_report_size_mb: int = 50
    
    # Configuración de logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Configuración de seguridad
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Configuración de límites
    max_upload_size_mb: int = 10
    max_events_per_request: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()
