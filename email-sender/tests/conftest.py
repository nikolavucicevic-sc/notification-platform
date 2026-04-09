import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import httpx

# Set test environment variables before importing app
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["REDIS_EMAIL_QUEUE"] = "email:queue"
os.environ["REDIS_DLQ_QUEUE"] = "email:dlq"
os.environ["WIREMOCK_URL"] = "http://localhost:8089"


@pytest.fixture
def mock_redis_queue():
    """Mock Redis queue for testing."""
    queue = MagicMock()
    queue.push = MagicMock(return_value=True)
    queue.pop = MagicMock(return_value=None)
    queue.close = MagicMock()
    return queue


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for email API calls."""
    client = AsyncMock(spec=httpx.AsyncClient)
    response = AsyncMock()
    response.status_code = 201
    response.json.return_value = {"messageId": "test-id"}
    client.post = AsyncMock(return_value=response)
    return client


@pytest.fixture
def sample_email_request():
    """Sample email request data."""
    return {
        "notification_id": str(uuid4()),
        "subject": "Test Subject",
        "body": "Test Body",
        "customer_ids": [str(uuid4()), str(uuid4())],
        "retry_count": 0
    }


@pytest.fixture
def sample_email_request_with_retries():
    """Email request with retry count."""
    return {
        "notification_id": str(uuid4()),
        "subject": "Test Subject",
        "body": "Test Body",
        "customer_ids": [str(uuid4())],
        "retry_count": 2
    }
