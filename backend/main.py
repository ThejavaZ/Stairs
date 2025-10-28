from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
import uvicorn
from contextlib import asynccontextmanager

from app.database import engine, Base, SessionLocal
from app.routers import eventos, cameras, turnos, estadisticas, configuracion
from app.config import settings
from app.services.detection_manager import detection_manager
from app.models import Camera

# Create log directory if it doesn't exist
log_dir = os.path.dirname(settings.log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file) if os.path.dirname(settings.log_file) else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    
    # Crear directorios necesarios
    os.makedirs(settings.reports_dir, exist_ok=True)
    os.makedirs("./temp", exist_ok=True)
    
    # Verificar modelo YOLO
    if not os.path.exists(settings.yolo_model_path):
        logger.warning(f"Modelo YOLO no encontrado en {settings.yolo_model_path}")
    
    # Start detection for all active cameras
    db = SessionLocal()
    active_cameras = db.query(Camera).filter(Camera.is_active == True).all()
    for camera in active_cameras:
        detection_manager.start_detection(camera, db)
    db.close()

    logger.info("Sistema iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    detection_manager.stop_all()


app = FastAPI(
    title=settings.app_name,
    description="API para detección de empleados usando OpenCV y YOLO con reportes automáticos",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + (["*"] if settings.debug else []),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "timestamp": datetime.now().isoformat()}
    )

# Include routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["Cameras"])
app.include_router(turnos.router, prefix="/api/turnos", tags=["Turnos"])
app.include_router(estadisticas.router, prefix="/api/estadisticas", tags=["Estadísticas"])
app.include_router(configuracion.router, prefix="/api/configuracion", tags=["Configuración"])
app.include_router(eventos.router, prefix="/api", tags=["Eventos"])

@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name} está funcionando",
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat(),
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    try:
        # Verificar base de datos
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Verificar modelo YOLO
    model_status = "healthy" if os.path.exists(settings.yolo_model_path) else "model_missing"
    
    return {
        "status": "healthy" if db_status == "healthy" and model_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "components": {
            "database": db_status,
            "yolo_model": model_status,
            "api": "healthy"
        },
        "uptime": "running"
    }

@app.get("/info")
async def system_info():
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug_mode": settings.debug,
        "database_type": "SQLite",
        "yolo_model": settings.yolo_model_path,
        "supported_formats": ["PDF", "Word", "Excel", "XML", "JSON"],
        "api_features": [
            "Employee Detection",
            "Safety Monitoring", 
            "Shift Management",
            "Report Generation",
            "Real-time Processing"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )