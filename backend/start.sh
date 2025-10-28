#!/bin/bash

# Employee Detection API Startup Script

echo "🚀 Iniciando Employee Detection API..."

# Create necessary directories
mkdir -p logs reports temp data

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Download YOLO model if not exists
if [ ! -f "yolov8n.pt" ]; then
    echo "🤖 Descargando modelo YOLO..."
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
fi

# Run database migrations (if any)
echo "🗄️ Configurando base de datos..."
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine); print('Base de datos configurada')"

# Start the application
echo "🌟 Iniciando servidor..."
echo "📊 API disponible en: http://localhost:8000"
echo "📖 Documentación en: http://localhost:8000/docs"
echo "🏥 Health check en: http://localhost:8000/health"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
