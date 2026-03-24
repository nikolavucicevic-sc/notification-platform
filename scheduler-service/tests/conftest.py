import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test database URL before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base, get_db
from app.main import app
from app.models.scheduled_notification import ScheduleType, RecurrenceType, JobStatus


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
def sample_schedule_data():
    """Sample schedule data for one-time notification."""
    return {
        "schedule_type": "ONCE",
        "scheduled_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "notification_type": "EMAIL",
        "subject": "Test Notification",
        "body": "This is a test notification",
        "customer_ids": [str(uuid4()), str(uuid4())],
        "created_by": "test_user"
    }


@pytest.fixture
def sample_recurring_schedule_data():
    """Sample schedule data for recurring notification."""
    return {
        "schedule_type": "RECURRING",
        "scheduled_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "recurrence_type": "DAILY",
        "recurrence_end_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "notification_type": "EMAIL",
        "subject": "Daily Reminder",
        "body": "This is a daily reminder",
        "customer_ids": [str(uuid4())],
        "created_by": "test_user"
    }


@pytest.fixture
def mock_scheduler():
    """Mock the APScheduler."""
    with patch('app.services.scheduler.scheduler') as mock:
        mock_job = Mock()
        mock_job.id = "test-job-id"
        mock_job.next_run_time = datetime.now() + timedelta(hours=1)
        mock.add_job.return_value = mock_job
        yield mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient for notification service calls."""
    with patch('app.services.scheduler.httpx.AsyncClient') as mock:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = AsyncMock()
        mock_client.__aenter__.return_value.post.return_value = mock_response
        mock.return_value = mock_client
        yield mock_client
