import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Set test environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"
os.environ["RABBITMQ_EMAIL_QUEUE"] = "email.send"
os.environ["RABBITMQ_STATUS_QUEUE"] = "email.status"

from app.database import Base, get_db
from app.main import app
from app.models.notification import NotificationStatus, NotificationType


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel for testing."""
    channel = AsyncMock()
    channel.default_exchange = MagicMock()
    channel.default_exchange.publish = AsyncMock()
    return channel


@pytest.fixture
def mock_rabbitmq_connection():
    """Mock RabbitMQ connection for testing."""
    connection = AsyncMock()
    channel = AsyncMock()
    connection.channel = AsyncMock(return_value=channel)
    return connection


@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing."""
    return {
        "notification_type": "EMAIL",
        "subject": "Test Subject",
        "body": "Test Body",
        "customer_ids": [str(uuid4()), str(uuid4())]
    }


@pytest.fixture
def sample_notification_minimal():
    """Minimal notification data for testing."""
    return {
        "notification_type": "EMAIL",
        "subject": "Test",
        "body": "Test body",
        "customer_ids": [str(uuid4())]
    }