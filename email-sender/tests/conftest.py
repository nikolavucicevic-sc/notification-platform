import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import httpx

# Set test environment variables before importing app
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"
os.environ["RABBITMQ_EMAIL_QUEUE"] = "email.send"
os.environ["RABBITMQ_STATUS_QUEUE"] = "email.status"
os.environ["WIREMOCK_URL"] = "http://localhost:8089"


@pytest.fixture
def mock_rabbitmq_channel():
    """Mock RabbitMQ channel for testing."""
    channel = AsyncMock()
    channel.default_exchange = MagicMock()
    channel.default_exchange.publish = AsyncMock()
    channel.basic_ack = AsyncMock()
    channel.basic_nack = AsyncMock()
    return channel


@pytest.fixture
def mock_rabbitmq_connection():
    """Mock RabbitMQ connection for testing."""
    connection = AsyncMock()
    channel = AsyncMock()
    connection.channel = AsyncMock(return_value=channel)
    return connection


@pytest.fixture
def mock_rabbitmq_message():
    """Mock RabbitMQ incoming message."""
    message = AsyncMock()
    message.body = b'{"notification_id": "123e4567-e89b-12d3-a456-426614174000", "subject": "Test", "body": "Test body", "customer_ids": ["123e4567-e89b-12d3-a456-426614174001"], "retry_count": 0}'
    message.delivery_tag = 1
    return message


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for email API calls."""
    client = AsyncMock(spec=httpx.AsyncClient)
    response = AsyncMock()
    response.status_code = 200
    response.json.return_value = {"success": True}
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
