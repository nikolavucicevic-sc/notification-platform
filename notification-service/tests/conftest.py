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

# Disable OpenTelemetry tracing before importing the app to prevent Jaeger connection attempts
from unittest.mock import patch as _patch
_tracing_patch = _patch("app.tracing.setup_tracing", return_value=None)
_tracing_patch.start()

from app.database import Base, get_db
from app.main import app
import app.main as app_main
from app.auth import get_current_user, require_operator_or_admin, require_admin, require_super_admin
from app.models.notification import NotificationStatus, NotificationType
from app.models.user import User, UserRole


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
def mock_operator_user():
    """A mock OPERATOR user — sufficient for notification endpoints."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.username = "test_operator"
    user.email = "operator@test.com"
    user.role = UserRole.OPERATOR
    user.is_active = True
    user.tenant_id = uuid4()
    user.email_limit = None
    user.sms_limit = None
    user.email_sent = 0
    user.sms_sent = 0
    return user


@pytest.fixture(scope="function")
def client(db_session, mock_operator_user):
    """Create a test client with database and auth dependency overrides."""
    import asyncio

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return mock_operator_user

    def override_require_operator_or_admin():
        return mock_operator_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_operator_or_admin] = override_require_operator_or_admin

    # Reset shutdown_event and pre-set it so the lifespan shutdown doesn't wait 30s
    app_main.shutdown_event = asyncio.Event()
    app_main.shutdown_event.set()

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
