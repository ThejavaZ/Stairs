# Employee Detection API

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-blueviolet.svg)](https://ultralytics.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)

API backend de alto rendimiento para la detección de empleados y el monitoreo de seguridad en el lugar de trabajo, utilizando FastAPI, OpenCV y YOLOv8.

## Descripción General

Este proyecto proporciona una solución backend completa para monitorear un área de trabajo a través de una cámara o imágenes estáticas. Utiliza el modelo de detección de objetos **YOLOv8** para identificar personas (empleados) y posibles infracciones de seguridad (faltas).

La aplicación está construida sobre **FastAPI**, lo que garantiza un alto rendimiento y una documentación de API interactiva y automática. Los eventos de detección se registran en una base de datos **SQLite** y el sistema es capaz de generar reportes diarios y por turno en múltiples formatos.

## ✨ Características Principales

- **Detección en Tiempo Real y por Imagen**: Procesa tanto imágenes estáticas (`/api/detect`) como capturas de cámara (`/api/detect/camera`).
- **Base de Datos de Eventos**: Utiliza **SQLAlchemy** para registrar cada evento de detección (fecha, hora, número de empleados, faltas) en una base de datos SQLite.
- **Gestión de Turnos**: Lógica de negocio para operar con tres turnos de trabajo (mañana, tarde, noche), asignando automáticamente cada evento al turno correspondiente.
- **Sistema de Reportes Avanzado**: Genera reportes detallados por día o por turno en múltiples formatos:
    - **PDF**: Con tablas y gráficos de resumen.
    - **Word (.docx)**: Documento profesional con tablas.
    - **Excel (.xlsx)**: Hojas de cálculo con datos y gráficos.
    - **XML**: Datos estructurados para integración con otros sistemas.
    - **JSON**: Formato ligero para consumo en APIs o frontends.
- **API RESTful Completa**: Endpoints para gestionar eventos, configuraciones, obtener estadísticas y generar reportes.
- **Configuración Flexible**: Gestiona toda la configuración de la aplicación (base de datos, rutas, umbrales de detección) a través de variables de entorno (`.env`).
- **Soporte para Docker**: Incluye `Dockerfile` y `docker-compose.yml` para un despliegue fácil y consistente.
- **Documentación Automática**: Gracias a FastAPI, la documentación interactiva de la API está disponible en `/docs` y `/redoc`.

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI, Uvicorn
- **Detección de Objetos**: YOLOv8, OpenCV
- **Base de Datos**: SQLAlchemy, SQLite
- **Validación de Datos**: Pydantic
- **Generación de Reportes**: ReportLab (PDF), python-docx (Word), openpyxl (Excel)
- **Contenerización**: Docker, Docker Compose
- **Testing**: Pytest, Pytest-Asyncio

## 📂 Estructura del Proyecto

```
.
├── app/                # Núcleo de la aplicación
│   ├── routers/        # Endpoints de la API (eventos.py)
│   ├── services/       # Lógica de negocio (vision.py, camera.py, reports.py)
│   ├── config.py       # Gestión de configuración (Pydantic)
│   ├── database.py     # Configuración de SQLAlchemy
│   ├── models.py       # Modelos de la base de datos (SQLAlchemy ORM)
│   ├── schemas.py      # Esquemas de datos (Pydantic)
│   └── utils.py        # Funciones de utilidad (ej. gestión de turnos)
├── logs/               # Archivos de log
├── reports/            # Reportes generados
├── tests/              # Pruebas unitarias y de integración
├── .env.example        # Archivo de ejemplo para variables de entorno
├── main.py             # Punto de entrada de la aplicación FastAPI
├── requirements.txt    # Dependencias de Python
├── Dockerfile          # Definición del contenedor Docker
├── docker-compose.yml  # Orquestación de servicios Docker
└── yolov8n.pt          # Pesos del modelo de detección
```

## 🚀 Instalación y Ejecución

### 1. Prerrequisitos

- Python 3.9 o superior
- Git

### 2. Clonar y Configurar el Entorno

```bash
# Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd employee-detection-backend/backend

# Crear y activar un entorno virtual
python -m venv .venv
# En Windows: 
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

La aplicación se configura mediante variables de entorno.

1.  Crea una copia del archivo de ejemplo:
    ```bash
    copy .env.example .env
    ```
2.  Modifica el archivo `.env` según sea necesario. Las variables más importantes son:
    - `DEBUG`: `true` para modo de desarrollo (activa docs y reload).
    - `DATABASE_URL`: URL de conexión a la base de datos.
    - `LOG_LEVEL`: Nivel de logging (e.g., `INFO`, `DEBUG`).
    - `CORS_ORIGINS`: Orígenes permitidos para CORS (ej. `http://localhost:3000` para un frontend en React).

### 4. Ejecutar la Aplicación

#### Localmente

Para iniciar el servidor en modo de desarrollo con recarga automática:

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`.

#### Con Docker

Para construir y ejecutar la aplicación usando Docker Compose:

```bash
docker-compose up --build
```

El servicio estará expuesto en el puerto `8000` del host.

## 🔌 API Endpoints

La base de todos los endpoints es `/api`.

| Método | Endpoint                               | Descripción                                                                                             |
| :----- | :------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| **Detección** |
| `POST` | `/detect`                              | Procesa una imagen subida para detectar empleados y faltas.                                             |
| `POST` | `/detect/camera`                       | Captura una imagen de la cámara, la procesa y devuelve el resultado.                                    |
| **Eventos** |
| `GET`  | `/eventos`                             | Lista todos los eventos con filtros (paginación, fecha, turno).                                         |
| `POST` | `/eventos`                             | Crea un nuevo evento de detección manualmente.                                                          |
| `DELETE`| `/eventos/{evento_id}`                 | Elimina un evento específico por su ID.                                                                 |
| **Reportes y Estadísticas** |
| `GET`  | `/eventos/{turno}`                     | Obtiene el reporte de un turno específico para una fecha dada.                                          |
| `GET`  | `/eventos/total/{fecha}`               | Obtiene el reporte consolidado de un día completo, incluyendo todos los turnos.                         |
| `GET`  | `/estadisticas/resumen`                | Devuelve estadísticas agregadas de los últimos N días (total de eventos, empleados, faltas, etc.).      |
| `GET`  | `/reportes/{formato}`                  | **(Muy útil)** Genera y descarga un reporte completo en el formato especificado (`pdf`, `word`, `excel`, `xml`, `json`). |
| `GET`  | `/reportes/preview/{formato}`          | Devuelve una vista previa en JSON de los datos que contendrá un reporte.                                |
| **Configuración** |
| `GET`  | `/configuracion`                       | Obtiene la configuración actual del sistema de detección.                                               |
| `PUT`  | `/configuracion/{nombre}`              | Actualiza un valor de configuración específico.                                                         |

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.