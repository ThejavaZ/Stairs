import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import ConfiguracionDeteccion

def test_get_shift_schedules(client: TestClient, db_session: Session):
    """Test retrieving shift schedules."""
    # Add some test data
    db_session.add(ConfiguracionDeteccion(nombre="turno_1_inicio", valor="06:00:00"))
    db_session.add(ConfiguracionDeteccion(nombre="turno_1_fin", valor="14:00:00"))
    db_session.commit()

    response = client.get("/shifts/")
    assert response.status_code == 200
    data = response.json()
    assert "turno_1" in data
    assert data["turno_1"]["inicio"] == "06:00:00"
    assert data["turno_1"]["fin"] == "14:00:00"
    # Test default values for other shifts
    assert "turno_2" in data
    assert data["turno_2"]["inicio"] == "14:00:00"

def test_update_shift_schedules(client: TestClient, db_session: Session):
    """Test updating shift schedules."""
    update_data = {
        "turno_1": {"inicio": "07:00:00", "fin": "15:00:00"},
        "turno_2": {"inicio": "15:00:00", "fin": "23:00:00"},
        "turno_3": {"inicio": "23:00:00", "fin": "07:00:00"}
    }
    response = client.put("/shifts/", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["turno_1"]["inicio"] == "07:00:00"
    assert data["turno_2"]["fin"] == "23:00:00"

    # Verify changes in the database
    turno_1_inicio = db_session.query(ConfiguracionDeteccion).filter_by(nombre="turno_1_inicio").one()
    assert turno_1_inicio.valor == "07:00:00"
    
    turno_3_fin = db_session.query(ConfiguracionDeteccion).filter_by(nombre="turno_3_fin").one()
    assert turno_3_fin.valor == "07:00:00"
