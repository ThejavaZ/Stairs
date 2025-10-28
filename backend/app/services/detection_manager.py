import threading
import time
from typing import Dict

from app.models import Camera
from app.services.vision import VisionService

class DetectionManager:
    def __init__(self):
        self.detection_threads: Dict[int, threading.Thread] = {}
        self.vision_services: Dict[int, VisionService] = {}
        self.stop_events: Dict[int, threading.Event] = {}

    def start_detection(self, camera: Camera, db_session):
        if camera.id in self.detection_threads and self.detection_threads[camera.id].is_alive():
            return

        stop_event = threading.Event()
        self.stop_events[camera.id] = stop_event

        vision_service = VisionService(camera, db_session, stop_event)
        self.vision_services[camera.id] = vision_service

        thread = threading.Thread(target=vision_service.run_detection)
        self.detection_threads[camera.id] = thread
        thread.start()

    def stop_detection(self, camera_id: int):
        if camera_id in self.stop_events:
            self.stop_events[camera_id].set()
            if camera_id in self.detection_threads:
                self.detection_threads[camera_id].join()
                del self.detection_threads[camera_id]
            if camera_id in self.vision_services:
                del self.vision_services[camera_id]
            del self.stop_events[camera_id]

    def stop_all(self):
        for camera_id in list(self.detection_threads.keys()):
            self.stop_detection(camera_id)

detection_manager = DetectionManager()
