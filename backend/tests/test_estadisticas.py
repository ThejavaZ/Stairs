import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import Evento
from app.schemas import TurnoEnum
from datetime import datetime, timedelta

def test_get_summary_statistics(client: TestClient, db_session: Session):
    """Test retrieving summary statistics."""
    # Clear existing events
    db_session.query(Evento).delete()
    db_session.commit()

    # Add some test events
    now = datetime.now()
    db_session.add(Evento(fecha_hora=now - timedelta(days=1), turno=TurnoEnum.MANANA, empleados=10, faltas=1, confianza=0.9))
    db_session.add(Evento(fecha_hora=now - timedelta(days=2), turno=TurnoEnum.TARDE, empleados=8, faltas=0, confianza=0.95))
    db_session.add(Evento(fecha_hora=now - timedelta(days=8), turno=TurnoEnum.NOCHE, empleados=5, faltas=2, confianza=0.8)) # This one is outside the default 7-day range
    db_session.commit()

    # Test with default 7 days
    response = client.get("/stats/resumen")
    assert response.status_code == 200
    data = response.json()
    
    assert data["periodo_dias"] == 7
    assert data["total_eventos"] == 2
    assert data["total_empleados"] == 18
    assert data["total_faltas"] == 1
    assert data["promedio_confianza"] == 0.92 # (0.9 + 0.95) / 2 = 0.925 -> rounded to 0.92
    assert "estadisticas_por_turno" in data
    assert data["estadisticas_por_turno"]["turno_1"]["empleados"] == 10
    assert data["estadisticas_por_turno"]["turno_2"]["empleados"] == 8
    assert data["estadisticas_por_turno"]["turno_3"]["empleados"] == 0

    # Test with a different day range
    response = client.get("/stats/resumen?dias=10")
    assert response.status_code == 200
    data = response.json()

    assert data["periodo_dias"] == 10
    assert data["total_eventos"] == 3
    assert data["total_empleados"] == 23
    assert data["total_faltas"] == 3
    assert data["promedio_confianza"] == 0.88 # (0.9 + 0.95 + 0.8) / 3 = 0.8833 -> rounded to 0.88
    assert data["estadisticas_por_turno"]["turno_3"]["empleados"] == 5
