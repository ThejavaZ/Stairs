import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from typing import List, Tuple, Dict, Optional
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.schemas import DetectionResult, TurnoEnum
from app.utils import obtener_turno_actual, validar_deteccion
from datetime import datetime
from app.models import Evento, Camera
from playsound import playsound
import threading
import time
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self, camera: Camera, db_session: Session, stop_event: threading.Event):
        self.camera = camera
        self.db_session = db_session
        self.stop_event = stop_event
        self.model = YOLO("yolov8n.pt")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=4,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.person_alerted = False
        self.last_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()

    def get_last_frame(self) -> Optional[np.ndarray]:
        with self.frame_lock:
            return self.last_frame

    def run_detection(self):
        rtsp_url = f"rtsp://{self.camera.username}:{self.camera.password}@{self.camera.ip_address}:{self.camera.port}"
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                time.sleep(1)
                cap.release()
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                continue

            # Detectar en el frame actual
            results = self.model.predict(frame, conf=0.5, iou=0.45, verbose=False)
            annotated_frame = results[0].plot()

            with self.frame_lock:
                self.last_frame = annotated_frame

        cap.release()
        cv2.destroyAllWindows()


    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        # YOLO detection of persons
        results = self.model(frame, verbose=False)
        persons = []
        for r in results[0].boxes:
            if int(r.cls) == 0:  # class 0 = person
                x1, y1, x2, y2 = r.xyxy[0].cpu().numpy().astype(int)
                persons.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        num_employees = len(persons)

        # MediaPipe hand detection
        hands_positions = []
        for (x1, y1, x2, y2) in persons:
            person_crop = frame[y1:y2, x1:x2]
            if person_crop.size == 0:
                continue

            rgb_crop = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            hand_results = self.hands.process(rgb_crop)

            if hand_results.multi_hand_landmarks:
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    h, w, _ = person_crop.shape
                    x = int(hand_landmarks.landmark[0].x * w) + x1
                    y = int(hand_landmarks.landmark[0].y * h) + y1
                    hands_positions.append((x, y))
                    cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)

        # Alert logic
        if self.camera.handrail_coordinates and self.camera.stairs_coordinates:
            handrail_left = self.camera.handrail_coordinates.get('left')
            handrail_right = self.camera.handrail_coordinates.get('right')
            stairs = self.camera.stairs_coordinates

            if handrail_left and handrail_right and stairs:
                cv2.rectangle(frame, (handrail_left['x1'], handrail_left['y1']), (handrail_left['x2'], handrail_left['y2']), (255, 0, 0), 2)
                cv2.rectangle(frame, (handrail_right['x1'], handrail_right['y1']), (handrail_right['x2'], handrail_right['y2']), (255, 0, 0), 2)
                cv2.rectangle(frame, (stairs['x1'], stairs['y1']), (stairs['x2'], stairs['y2']), (0, 255, 0), 2)

                valid_hands = 0
                for (x, y) in hands_positions:
                    if (handrail_left['x1'] < x < handrail_left['x2'] and handrail_left['y1'] < y < handrail_left['y2']) or \
                       (handrail_right['x1'] < x < handrail_right['x2'] and handrail_right['y1'] < y < handrail_right['y2']):
                        valid_hands += 1

                persons_on_stairs = 0
                for (x1, y1, x2, y2) in persons:
                    if (stairs['x1'] < (x1+x2)/2 < stairs['x2'] and stairs['y1'] < y2 < stairs['y2']):
                        persons_on_stairs += 1

                if persons_on_stairs > 0 and valid_hands == 0:
                    if not self.person_alerted:
                        self.trigger_alert(num_employees)
                        self.person_alerted = True
                else:
                    self.person_alerted = False
        return frame

    def trigger_alert(self, num_employees: int):
        try:
            playsound('backend/public/alert.mp3')
        except Exception as e:
            logger.error(f"Error playing sound: {e}")

        db_evento = Evento(
            empleados=num_employees,
            faltas=num_employees,
            turno=obtener_turno_actual(self.db_session),
            descripcion="Persona sin manos en barandal",
            confianza=100,
            camera_id=self.camera.id
        )
        self.db_session.add(db_evento)
        self.db_session.commit()

    def alert_off(self):
        url = f'http://{self.camera.ip_address}/api/control?alert=000000'# apagar alarma
        try:
            response = requests.get(url)

            if response.status_code == 200:
                posts = response.json()
                return posts
            else:
                print('Error:', response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print('Error:', e)
            return None

    def alert_on(self):
        url = f"http://{self.camera.ip_address}/api/control?alert=100001"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("Alert sound triggered successfully via API")
                posts = response.json()
                return posts
            logger.error(f"Failed to trigger alert sound via API, status code: {response.status_code}")


        except Exception as e:
            print(f"Error playing sound: {e}")
            return None

# Keep the old service for now
class EmployeeDetectionService:
    """
    Servicio de detección de empleados usando YOLO y OpenCV.
    Detecta empleados en escaleras y verifica el uso correcto del barandal.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa el servicio de detección.
        
        Args:
            model_path: Ruta al modelo YOLO personalizado. Si es None, usa YOLOv8n por defecto.
        """
        self.model_path = model_path or "yolov8n.pt"
        self.model = None
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45
        self.load_model()
        
        # Clases de interés (COCO dataset)
        self.person_class_id = 0  # Persona en COCO dataset
        
        # Configuración de detección
        self.handrail_detection_enabled = True
        self.stair_detection_enabled = True
        
    def load_model(self):
        """Carga el modelo YOLO."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Modelo YOLO cargado exitosamente: {self.model_path}")
        except Exception as e:
            logger.error(f"Error cargando modelo YOLO: {e}")
            raise
    
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Detecta objetos en la imagen usando YOLO.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            Lista de detecciones con bbox, confianza y clase
        """
        if self.model is None:
            raise ValueError("Modelo YOLO no está cargado")
        
        results = self.model(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(confidence),
                        'class_id': class_id,
                        'class_name': self.model.names[class_id]
                    })
        
        return detections
    
    def detect_handrail(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta barandales en la imagen usando procesamiento de imágenes.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            Lista de bounding boxes de barandales detectados
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro Gaussian para reducir ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detectar bordes usando Canny
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Detectar líneas usando HoughLinesP
        lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )
        
        handrails = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Filtrar líneas horizontales o casi horizontales (barandales)
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 30 or angle > 150:  # Líneas horizontales
                    # Crear bounding box para la línea
                    margin = 20
                    bbox = [
                        min(x1, x2) - margin,
                        min(y1, y2) - margin,
                        max(x1, x2) + margin,
                        max(y1, y2) + margin
                    ]
                    handrails.append(tuple(bbox))
        
        return handrails
    
    def detect_stairs(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta escaleras en la imagen.
        
        Args:
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            Lista de bounding boxes de escaleras detectadas
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro para detectar patrones de escaleras
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        
        # Detectar líneas horizontales (escalones)
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=50,
            maxLineGap=5
        )
        
        stairs = []
        if lines is not None:
            # Agrupar líneas horizontales cercanas
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 15:  # Líneas muy horizontales
                    horizontal_lines.append((y1 + y2) // 2)  # Promedio Y
            
            if len(horizontal_lines) >= 3:  # Al menos 3 escalones
                horizontal_lines.sort()
                # Crear bounding box para toda la escalera
                y_min = min(horizontal_lines) - 50
                y_max = max(horizontal_lines) + 50
                stairs.append((0, max(0, y_min), image.shape[1], min(image.shape[0], y_max)))
        
        return stairs
    
    def is_person_holding_handrail(self, person_bbox: List[int], handrails: List[Tuple[int, int, int, int]]) -> bool:
        """
        Determina si una persona está agarrando el barandal.
        
        Args:
            person_bbox: Bounding box de la persona [x1, y1, x2, y2]
            handrails: Lista de bounding boxes de barandales
            
        Returns:
            True si la persona está agarrando el barandal
        """
        if not handrails:
            return False
        
        px1, py1, px2, py2 = person_bbox
        person_center_x = (px1 + px2) // 2
        person_hand_y = py1 + int((py2 - py1) * 0.4)  # Aproximadamente donde estarían las manos
        
        for hx1, hy1, hx2, hy2 in handrails:
            # Verificar si las manos están cerca del barandal
            if (hx1 <= person_center_x <= hx2 and 
                abs(person_hand_y - ((hy1 + hy2) // 2)) < 50):
                return True
        
        return False
    
    def is_person_on_stairs(self, person_bbox: List[int], stairs: List[Tuple[int, int, int, int]]) -> bool:
        """
        Determina si una persona está en las escaleras.
        
        Args:
            person_bbox: Bounding box de la persona [x1, y1, x2, y2]
            stairs: Lista de bounding boxes de escaleras
            
        Returns:
            True si la persona está en las escaleras
        """
        if not stairs:
            return False
        
        px1, py1, px2, py2 = person_bbox
        person_bottom = py2
        person_center_x = (px1 + px2) // 2
        
        for sx1, sy1, sx2, sy2 in stairs:
            # Verificar si la persona está dentro del área de escaleras
            if (sx1 <= person_center_x <= sx2 and 
                sy1 <= person_bottom <= sy2):
                return True
        
        return False
    
    def process_image(self, db: Session, image: np.ndarray) -> DetectionResult:
        """
        Procesa una imagen y retorna los resultados de detección.
        
        Args:
            db: Sesión de la base de datos
            image: Imagen en formato numpy array (BGR)
            
        Returns:
            DetectionResult con empleados y faltas detectadas
        """
        try:
            # Detectar objetos con YOLO
            detections = self.detect_objects(image)
            
            # Filtrar solo personas
            persons = [d for d in detections if d['class_id'] == self.person_class_id]
            
            # Detectar barandales y escaleras
            handrails = self.detect_handrail(image) if self.handrail_detection_enabled else []
            stairs = self.detect_stairs(image) if self.stair_detection_enabled else []
            
            empleados_detectados = 0
            faltas_detectadas = 0
            descripciones = []
            confianzas = []
            
            for person in persons:
                bbox = person['bbox']
                confidence = person['confidence']
                confianzas.append(confidence)
                
                is_on_stairs = self.is_person_on_stairs(bbox, stairs)
                is_holding_handrail = self.is_person_holding_handrail(bbox, handrails)
                
                if is_on_stairs:
                    empleados_detectados += 1
                    if not is_holding_handrail:
                        faltas_detectadas += 1
                        descripciones.append(f"Empleado en escalera sin agarrar barandal (confianza: {confidence:.2f})")
                    else:
                        descripciones.append(f"Empleado en escalera agarrando barandal correctamente (confianza: {confidence:.2f})")
                elif is_holding_handrail:
                    empleados_detectados += 1
                    descripciones.append(f"Empleado agarrando barandal (confianza: {confidence:.2f})")
            
            # Validar resultados
            if not validar_deteccion(empleados_detectados, faltas_detectadas):
                logger.warning("Detección inválida, ajustando resultados")
                faltas_detectadas = min(faltas_detectadas, empleados_detectados)
            
            # Calcular confianza promedio
            confianza_promedio = int(np.mean(confianzas) * 100) if confianzas else 0
            
            descripcion_final = "; ".join(descripciones) if descripciones else "No se detectaron empleados"
            
            return DetectionResult(
                empleados_detectados=empleados_detectados,
                faltas_detectadas=faltas_detectadas,
                descripcion=descripcion_final,
                confianza=confianza_promedio,
                turno_actual=obtener_turno_actual(db),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return DetectionResult(
                empleados_detectados=0,
                faltas_detectadas=0,
                descripcion=f"Error en procesamiento: {str(e)}",
                confianza=0,
                turno_actual=obtener_turno_actual(db),
                timestamp=datetime.now()
            )
    
    def process_video_frame(self, db: Session, frame: np.ndarray) -> DetectionResult:
        """
        Procesa un frame de video.
        
        Args:
            db: Sesión de la base de datos
            frame: Frame de video en formato numpy array (BGR)
            
        Returns:
            DetectionResult con empleados y faltas detectadas
        """
        return self.process_image(db, frame)
    
    def draw_detections(self, image: np.ndarray, result: DetectionResult) -> np.ndarray:
        """
        Dibuja las detecciones en la imagen para visualización.
        
        Args:
            image: Imagen original
            result: Resultado de detección
            
        Returns:
            Imagen con detecciones dibujadas
        """
        annotated_image = image.copy()
        
        # Detectar objetos para dibujar
        detections = self.detect_objects(image)
        persons = [d for d in detections if d['class_id'] == self.person_class_id]
        
        # Dibujar personas detectadas
        for person in persons:
            x1, y1, x2, y2 = person['bbox']
            confidence = person['confidence']
            
            # Color verde para empleados seguros, rojo para faltas
            color = (0, 255, 0)  # Verde por defecto
            if result.faltas_detectadas > 0:
                color = (0, 0, 255)  # Rojo si hay faltas
            
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                annotated_image,
                f"Empleado {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        # Agregar información del resultado
        info_text = f"Empleados: {result.empleados_detectados}, Faltas: {result.faltas_detectadas}"
        cv2.putText(
            annotated_image,
            info_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        return annotated_image

# Instancia global del servicio
detection_service = EmployeeDetectionService()