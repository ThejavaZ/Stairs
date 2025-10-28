from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import cv2
import io

from app.database import get_db
from app.models import Camera, Evento
from app.schemas import CameraCreate, CameraUpdate, CameraResponse, DetectionResult, CameraCoordinates
from app.services.camera import CameraService
from app.services.detection_manager import detection_manager

router = APIRouter()

@router.post("/", response_model=CameraResponse, status_code=201)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """
    Adds a new camera to the system.
    """
    db_camera = db.query(Camera).filter(Camera.name == camera.name).first()
    if db_camera:
        raise HTTPException(status_code=400, detail=f"Camera with name '{camera.name}' already exists.")
    
    new_camera = Camera(**camera.dict())
    db.add(new_camera)
    db.commit()
    db.refresh(new_camera)

    if new_camera.is_active:
        detection_manager.start_detection(new_camera, db)

    return new_camera

@router.get("/", response_model=List[CameraResponse])
def list_cameras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Lists all configured cameras.
    """
    cameras = db.query(Camera).offset(skip).limit(limit).all()
    return cameras

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details for a specific camera.
    """
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera: CameraUpdate, db: Session = Depends(get_db)):
    """
    Updates a camera's details.
    """
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = camera.dict(exclude_unset=True)
    
    # Check for name conflict
    if "name" in update_data and update_data["name"] != db_camera.name:
        existing_camera = db.query(Camera).filter(Camera.name == update_data["name"]).first()
        if existing_camera:
            raise HTTPException(status_code=400, detail=f"Camera name '{update_data['name']}' is already in use.")

    if 'is_active' in update_data:
        if update_data['is_active']:
            detection_manager.start_detection(db_camera, db)
        else:
            detection_manager.stop_detection(camera_id)

    for key, value in update_data.items():
        setattr(db_camera, key, value)
    
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.put("/{camera_id}/coordinates", response_model=CameraResponse)
def update_camera_coordinates(camera_id: int, coordinates: CameraCoordinates, db: Session = Depends(get_db)):
    """
    Updates a camera's coordinates for handrails and stairs.
    """
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = coordinates.dict(exclude_unset=True)
    if 'handrail_left' in update_data or 'handrail_right' in update_data:
        db_camera.handrail_coordinates = {
            'left': update_data.get('handrail_left'),
            'right': update_data.get('handrail_right')
        }
    if 'stairs' in update_data:
        db_camera.stairs_coordinates = update_data.get('stairs')

    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@router.delete("/{camera_id}", status_code=200)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Deletes a camera from the system.
    """
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    detection_manager.stop_detection(camera_id)

    db.delete(db_camera)
    db.commit()
    return {"message": f"Camera '{db_camera.name}' (ID: {camera_id}) deleted successfully."}

@router.post("/{camera_id}/detect", response_model=DetectionResult)
async def detect_from_camera(
    camera_id: int,
    guardar_evento: bool = Query(True, description="Guardar resultado como evento en BD"),
    db: Session = Depends(get_db)
):
    """
    Captures a frame from the specified camera, processes it for employee detection,
    and optionally saves the event.
    """
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")

    if not db_camera.is_active:
        raise HTTPException(status_code=400, detail="Camera is not active")

    # Construct RTSP URL with port
    rtsp_url = f"rtsp://{db_camera.username}:{db_camera.password}@{db_camera.ip_address}:{db_camera.port}"
    
    # Instantiate CameraService and process
    camera_service_instance = CameraService()
    result = camera_service_instance.capture_and_process_from_source(rtsp_url, db)

    if result is None:
        raise HTTPException(
            status_code=500,
            detail=f"Could not capture or process frame from camera ID {camera_id} ({db_camera.name}). Check camera connection and credentials."
        )

    # Save event if requested and detection occurred
    if guardar_evento and (result.empleados_detectados > 0 or result.faltas_detectadas > 0):
        db_evento = Evento(
            empleados=result.empleados_detectados,
            faltas=result.faltas_detectadas,
            turno=result.turno_actual,
            descripcion=result.descripcion,
            confianza=result.confianza
        )
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)

    return result

async def generate_frames(camera_id: int):
    vision_service = detection_manager.vision_services.get(camera_id)
    if not vision_service:
        return

    while True:
        frame = vision_service.get_last_frame()
        if frame is not None:
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@router.get("/{camera_id}/stream")
async def stream_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Provides a live video stream from the specified camera.
    """
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")
