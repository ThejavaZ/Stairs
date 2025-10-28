import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Evento, Camera
from app.schemas import TurnoEnum
from datetime import datetime, timedelta, date
from unittest.mock import patch, MagicMock
import io

def test_list_events(client: TestClient, db_session: Session):
    """Test listing events with filters."""
    db_session.query(Evento).delete()
    db_session.commit()
    
    cam = Camera(name="EventCam", ip_address="8.8.8.8", port=123)
    db_session.add(cam)
    db_session.commit()

    db_session.add(Evento(fecha_hora=datetime(2023, 10, 26, 10, 0), turno=TurnoEnum.MANANA, empleados=5, faltas=0, camera_id=cam.id))
    db_session.add(Evento(fecha_hora=datetime(2023, 10, 26, 15, 0), turno=TurnoEnum.TARDE, empleados=4, faltas=1))
    db_session.add(Evento(fecha_hora=datetime(2023, 10, 25, 22, 0), turno=TurnoEnum.NOCHE, empleados=2, faltas=0))
    db_session.commit()

    # Test no filters
    response = client.get("/events/eventos")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Test filter by turno
    response = client.get("/events/eventos?turno=MANANA")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["turno"] == "MANANA"

    # Test filter by date range
    response = client.get("/events/eventos?fecha_inicio=2023-10-26T00:00:00&fecha_fin=2023-10-26T12:00:00")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Test filter by camera_id
    response = client.get(f"/events/eventos?camera_id={cam.id}")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_create_event(client: TestClient, db_session: Session):
    """Test creating an event manually."""
    event_data = {
        "fecha_hora": "2023-10-27T10:00:00",
        "turno": "MANANA",
        "empleados": 7,
        "faltas": 1,
        "confianza": 0.98,
        "descripcion": "Manual event"
    }
    response = client.post("/events/eventos", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["empleados"] == 7
    assert data["descripcion"] == "Manual event"

    # Test invalid data
    invalid_event_data = {"empleados": 5, "faltas": 6}
    response = client.post("/events/eventos", json=invalid_event_data)
    assert response.status_code == 400 # Validation error

def test_delete_event(client: TestClient, db_session: Session):
    """Test deleting an event."""
    evento = Evento(empleados=1, faltas=0, turno=TurnoEnum.MANANA)
    db_session.add(evento)
    db_session.commit()

    response = client.delete(f"/events/eventos/{evento.id_evento}")
    assert response.status_code == 204

    # Verify deletion
    deleted_evento = db_session.query(Evento).filter_by(id_evento=evento.id_evento).first()
    assert deleted_evento is None

    # Test deleting non-existent event
    response = client.delete("/events/eventos/9999")
    assert response.status_code == 404

@patch('app.routers.eventos.detection_service')
def test_detect_from_image_mocked(mock_detection_service, client: TestClient, db_session: Session):
    """Test image detection with a mocked service."""
    mock_result = MagicMock()
    mock_result.empleados_detectados = 2
    mock_result.faltas_detectadas = 0
    mock_result.turno_actual = "TARDE"
    mock_result.descripcion = "Image detection"
    mock_result.confianza = 0.88
    mock_detection_service.process_image.return_value = mock_result

    # Create a fake image file
    fake_image = io.BytesIO(b"fake image data")
    
    response = client.post("/events/detect", files={"file": ("test.jpg", fake_image, "image/jpeg")})
    
    assert response.status_code == 200
    data = response.json()
    assert data["empleados_detectados"] == 2
    assert data["descripcion"] == "Image detection"

    # Verify that an event was created in the DB
    events = db_session.query(Evento).filter(Evento.descripcion == "Image detection").all()
    assert len(events) == 1

def test_get_report_preview(client: TestClient, db_session: Session):
    """Test the report preview endpoint."""
    db_session.query(Evento).delete()
    db_session.commit()
    db_session.add(Evento(fecha_hora=datetime.now() - timedelta(hours=1), turno=TurnoEnum.TARDE, empleados=10, faltas=2))
    db_session.commit()

    today = date.today().isoformat()
    response = client.get(f"/events/reportes/preview?fecha_inicio={today}&fecha_fin={today}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_empleados"] == 10
    assert data["total_faltas"] == 2
    assert len(data["turnos"]) > 0

@patch('app.routers.eventos.report_generator')
def test_generate_report_mocked(mock_report_generator, client: TestClient, db_session: Session):
    """Test report generation with a mocked generator."""
    mock_report_generator.generate_pdf_report.return_value = b"fake pdf content"
    mock_report_generator.generate_word_report.return_value = b"fake word content"

    # Test PDF report
    response = client.get("/events/reportes/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"fake pdf content"

    # Test Word report
    response = client.get("/events/reportes/word")
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in response.headers["content-type"]
    assert response.content == b"fake word content"

    # Test unsupported format
    response = client.get("/events/reportes/unsupported")
    assert response.status_code == 400
