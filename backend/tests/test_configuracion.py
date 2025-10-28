import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import ConfiguracionDeteccion

def test_get_configuration(client: TestClient, db_session: Session):
    """Test retrieving the system configuration."""
    # Add a test configuration to the database
    db_session.add(ConfiguracionDeteccion(nombre="confidence_threshold", valor="0.6"))
    db_session.commit()

    response = client.get("/config/")
    assert response.status_code == 200
    data = response.json()
    assert "confidence_threshold" in data
    assert data["confidence_threshold"] == "0.6"
    # Test default value for a key that is not in the DB
    assert "iou_threshold" in data
    assert data["iou_threshold"] == "0.45"

def test_update_configuration(client: TestClient, db_session: Session):
    """Test updating a configuration setting."""
    # Test updating an existing setting
    config_item = ConfiguracionDeteccion(nombre="iou_threshold", valor="0.5")
    db_session.add(config_item)
    db_session.commit()

    response = client.put("/config/iou_threshold?valor=0.55")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Configuración 'iou_threshold' actualizada"
    assert data["config"]["valor"] == "0.55"

    # Verify the change in the database
    updated_item = db_session.query(ConfiguracionDeteccion).filter_by(nombre="iou_threshold").one()
    assert updated_item.valor == "0.55"

    # Test creating a new setting
    response = client.put("/config/new_setting?valor=new_value&descripcion=A new test setting")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Configuración 'new_setting' actualizada"
    
    new_item = db_session.query(ConfiguracionDeteccion).filter_by(nombre="new_setting").one_or_none()
    assert new_item is not None
    assert new_item.valor == "new_value"
    assert new_item.descripcion == "A new test setting"
