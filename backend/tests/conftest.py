import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app
from alembic.config import Config
from alembic import command

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Alembic configuration
alembic_cfg = Config("C:\\Users\\JavierSG\\OneDrive\\Escritorio\\Stairs\\alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # This fixture will run once per test session
    # It will create the schema and then it will be used for all tests
    command.upgrade(alembic_cfg, "head")
    yield
    # You could add a downgrade step here if needed, but for an in-memory db it's not necessary

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
