import pytest
import numpy as np
import cv2
from app.services.vision import detection_service

def test_detection_service_initialization():
    """Test that detection service initializes properly."""
    assert detection_service.model is not None
    assert detection_service.confidence_threshold > 0
    assert detection_service.iou_threshold > 0

def test_process_dummy_image():
    """Test processing a dummy image."""
    # Create a dummy image
    dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Process the image
    result = detection_service.process_image(dummy_image)
    
    # Check result structure
    assert hasattr(result, 'empleados_detectados')
    assert hasattr(result, 'faltas_detectadas')
    assert hasattr(result, 'descripcion')
    assert hasattr(result, 'confianza')
    assert hasattr(result, 'turno_actual')

def test_detection_validation():
    """Test detection validation logic."""
    from app.utils import validar_deteccion
    
    # Valid cases
    assert validar_deteccion(5, 2) == True
    assert validar_deteccion(0, 0) == True
    assert validar_deteccion(10, 10) == True
    
    # Invalid cases
    assert validar_deteccion(-1, 0) == False
    assert validar_deteccion(0, -1) == False
    assert validar_deteccion(5, 10) == False  # More faults than employees
