import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Camera

# Mock the detection manager before it's imported by the router
mock_detection_manager = MagicMock()

# Create a mock for the VisionService
mock_vision_service = MagicMock()
mock_vision_service.get_last_frame.return_value = None # Default to no frame

# When get is called on vision_services, return our mock
mock_detection_manager.vision_services.get.return_value = mock_vision_service


with patch('app.services.detection_manager.detection_manager', mock_detection_manager):
    from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_create_camera(client: TestClient, db_session: Session):
    """Test creating a new camera."""
    camera_data = {
        "name": "Test Camera",
        "ip_address": "192.168.1.100",
        "port": 554,
        "username": "user",
        "password": "password",
        "is_active": True
    }
    response = client.post("/cameras/", json=camera_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == camera_data["name"]
    assert data["ip_address"] == camera_data["ip_address"]
    assert data["is_active"] is True
    
    # Verify it was added to the DB
    db_camera = db_session.query(Camera).filter(Camera.id == data["id"]).first()
    assert db_camera is not None
    assert db_camera.name == "Test Camera"

    # Test creating a camera with a duplicate name
    response = client.post("/cameras/", json=camera_data)
    assert response.status_code == 400

def test_list_cameras(client: TestClient, db_session: Session):
    """Test listing all cameras."""
    # Clear cameras and add a known one
    db_session.query(Camera).delete()
    db_session.commit()
    db_session.add(Camera(name="Cam 1", ip_address="1.1.1.1", port=554, username="u", password="p"))
    db_session.commit()

    response = client.get("/cameras/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "Cam 1"

def test_get_camera(client: TestClient, db_session: Session):
    """Test retrieving a single camera."""
    camera = Camera(name="FindMe", ip_address="2.2.2.2", port=554, username="u", password="p")
    db_session.add(camera)
    db_session.commit()

    response = client.get(f"/cameras/{camera.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FindMe"

    # Test getting a non-existent camera
    response = client.get("/cameras/9999")
    assert response.status_code == 404

def test_update_camera(client: TestClient, db_session: Session):
    """Test updating a camera's details."""
    camera = Camera(name="OriginalName", ip_address="3.3.3.3", port=554, username="u", password="p")
    db_session.add(camera)
    db_session.commit()

    update_data = {"name": "UpdatedName", "is_active": False}
    response = client.put(f"/cameras/{camera.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedName"
    assert data["is_active"] is False

    # Verify the update in the database
    db_session.refresh(camera)
    assert camera.name == "UpdatedName"

def test_delete_camera(client: TestClient, db_session: Session):
    """Test deleting a camera."""
    camera = Camera(name="ToDelete", ip_address="4.4.4.4", port=554, username="u", password="p")
    db_session.add(camera)
    db_session.commit()

    response = client.delete(f"/cameras/{camera.id}")
    assert response.status_code == 200
    
    # Verify it's deleted from the DB
    deleted_camera = db_session.query(Camera).filter(Camera.id == camera.id).first()
    assert deleted_camera is None

    # Test deleting a non-existent camera
    response = client.delete("/cameras/9999")
    assert response.status_code == 404

def test_update_camera_coordinates(client: TestClient, db_session: Session):
    """Test updating camera coordinates."""
    camera = Camera(name="CoordCam", ip_address="5.5.5.5", port=554, username="u", password="p")
    db_session.add(camera)
    db_session.commit()

    coords_data = {
        "handrail_left": [[1,2], [3,4]],
        "handrail_right": [[5,6], [7,8]],
        "stairs": [[[1,1],[2,2],[3,3],[4,4]]]
    }
    response = client.put(f"/cameras/{camera.id}/coordinates", json=coords_data)
    assert response.status_code == 200
    data = response.json()
    assert data["handrail_coordinates"]["left"] == [[1,2], [3,4]]
    assert data["stairs_coordinates"][0][0] == [1,1]

@patch('app.routers.cameras.CameraService')
def test_detect_from_camera_mocked(mock_camera_service, client: TestClient, db_session: Session):
    """Test detection from a camera with a mocked service."""
    # Mock the service instance and its method
    mock_instance = mock_camera_service.return_value
    mock_result = MagicMock()
    mock_result.empleados_detectados = 1
    mock_result.faltas_detectadas = 0
    mock_result.turno_actual = "MAÑANA"
    mock_result.descripcion = "Test detection"
    mock_result.confianza = 0.95
    mock_instance.capture_and_process_from_source.return_value = mock_result

    camera = Camera(name="DetectCam", ip_address="6.6.6.6", port=554, username="u", password="p", is_active=True)
    db_session.add(camera)
    db_session.commit()

    response = client.post(f"/cameras/{camera.id}/detect")
    assert response.status_code == 200
    data = response.json()
    assert data["empleados_detectados"] == 1
    assert data["descripcion"] == "Test detection"

def test_stream_camera(client: TestClient, db_session: Session):
    """Test the camera stream endpoint."""
    camera = Camera(name="StreamCam", ip_address="7.7.7.7", port=554, username="u", password="p", is_active=True)
    db_session.add(camera)
    db_session.commit()
    
    # Start detection for this camera to ensure vision_service is created
    mock_detection_manager.start_detection(camera, db_session)

    response = client.get(f"/cameras/{camera.id}/stream")
    assert response.status_code == 200
    assert "multipart/x-mixed-replace" in response.headers["content-type"]
