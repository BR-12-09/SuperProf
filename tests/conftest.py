# app/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import BaseSQL, get_db
from app.services.auth import hash_password
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.booking import Booking

@pytest.fixture(scope="session")
def test_engine():
    # ✅ Une SEULE connexion partagée pour toute la session de tests
    engine = create_engine(
        "sqlite://",  # ⬅️ pas /:memory:/ avec StaticPool
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # ⬅️ clé : même connexion pour tous
    )
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    # On repart propre à chaque test
    BaseSQL.metadata.drop_all(bind=test_engine)
    BaseSQL.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

# Override FastAPI dependency pour utiliser NOTRE session de test
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function")
def tutor_user(db_session):
    u = User(
        first_name="Alice", last_name="Tutor",
        email="alice.tutor@test.com",
        role=UserRole.tutor,
        hashed_password=hash_password("pass"),
    )
    db_session.add(u); db_session.commit(); db_session.refresh(u)
    return u

@pytest.fixture(scope="function")
def student_user(db_session):
    u = User(
        first_name="Bob", last_name="Student",
        email="bob.student@test.com",
        role=UserRole.student,
        hashed_password=hash_password("pass"),
    )
    db_session.add(u); db_session.commit(); db_session.refresh(u)
    return u
