import cv2
import numpy as np
from typing import Optional
import logging
import base64
from app.services.vision import detection_service
from app.schemas import DetectionResult

logger = logging.getLogger(__name__)

class CameraService:
    """
    Servicio para manejar la captura de imágenes desde diversas fuentes (cámaras locales, URLs RTSP).
    """

    def capture_and_process_from_source(self, source: str | int, db) -> Optional[DetectionResult]:
        """
        Captura un único frame desde una fuente de video, lo procesa y retorna el resultado.

        Args:
            source: ID de la cámara (int) o URL del stream (str).

        Returns:
            DetectionResult si la captura y procesamiento son exitosos, de lo contrario None.
        """
        cap = None
        try:
            logger.info(f"Intentando abrir la fuente de video: {source}")
            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                logger.error(f"No se pudo abrir la fuente de video: {source}")
                return None

            ret, frame = cap.read()

            if not ret or frame is None:
                logger.warning(f"No se pudo capturar un frame válido desde: {source}")
                return None
            
            logger.info(f"Frame capturado exitosamente desde: {source}")
            
            # Procesar el frame con el servicio de detección
            result = detection_service.process_video_frame(db, frame)

            # Dibujar detecciones y codificar imagen
            if result:
                annotated_frame = detection_service.draw_detections(frame, result)
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                result.image_base64 = base64.b64encode(buffer).decode('utf-8')

            return result

        except Exception as e:
            logger.error(f"Error durante la captura o procesamiento desde '{source}': {e}", exc_info=True)
            return None
        
        finally:
            if cap is not None:
                cap.release()
                logger.info(f"Fuente de video '{source}' liberada.")