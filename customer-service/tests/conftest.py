import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

from app.database import Base, get_db
from app.main import app
from app.auth import get_current_tenant_id

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

FAKE_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def _create_tables(eng):
    """Create tenants stub first (FK target), then all app tables."""
    with eng.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """))
        conn.execute(text(
            "INSERT OR IGNORE INTO tenants (id, name) VALUES (:id, :name)"
        ), {"id": FAKE_TENANT_ID, "name": "Test Tenant"})
        conn.commit()
    Base.metadata.create_all(bind=eng)


@pytest.fixture(scope="function")
def db_session():
    _create_tables(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS tenants"))
            conn.commit()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Bypass JWT auth — inject a fixed tenant context
    def override_auth():
        return (FAKE_TENANT_ID, "ADMIN")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_tenant_id] = override_auth

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer_data():
    return {
        "email": "test@example.com",
        "phone_number": "+38164123456",
        "first_name": "John",
        "last_name": "Doe"
    }


@pytest.fixture
def sample_customer_data_no_phone():
    return {
        "email": "test2@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
    }
