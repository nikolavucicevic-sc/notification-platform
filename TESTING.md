# Testing Guide

This document provides comprehensive information about the test suite for the Notification Platform.

## Table of Contents
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)

## Overview

The Notification Platform has comprehensive test coverage across all three microservices:
- **Customer Service**: API endpoints, database operations, and model tests
- **Notification Service**: API endpoints, database operations, messaging, and model tests
- **Email Sender**: Email client, message consumers, and DLQ handler tests

### Testing Framework
- **pytest**: Main testing framework
- **pytest-asyncio**: For testing async functions
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking utilities
- **httpx**: HTTP client testing (already installed)

## Test Structure

```
notification-platform/
├── customer-service/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test fixtures and configuration
│   │   ├── test_api.py          # API endpoint tests
│   │   └── test_models.py       # Database model tests
│   └── pytest.ini
│
├── notification-service/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test fixtures and configuration
│   │   ├── test_api.py          # API endpoint tests
│   │   ├── test_models.py       # Database model tests
│   │   └── test_messaging.py    # RabbitMQ messaging tests
│   └── pytest.ini
│
├── email-sender/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test fixtures and configuration
│   │   ├── test_email_client.py # Email client tests
│   │   ├── test_consumer.py     # Message consumer tests
│   │   └── test_dlq_handler.py  # Dead-letter queue handler tests
│   └── pytest.ini
│
└── run-tests.sh                 # Convenience script to run all tests
```

## Running Tests

### Prerequisites
1. Install dependencies for each service:
   ```bash
   cd customer-service && pip install -r requirements.txt && cd ..
   cd notification-service && pip install -r requirements.txt && cd ..
   cd email-sender && pip install -r requirements.txt && cd ..
   ```

### Run All Tests
Use the convenience script:
```bash
./run-tests.sh
```

### Run Tests for Individual Services

**Customer Service:**
```bash
cd customer-service
pytest -v
```

**Notification Service:**
```bash
cd notification-service
pytest -v
```

**Email Sender:**
```bash
cd email-sender
pytest -v
```

### Run Tests with Coverage
```bash
cd customer-service
pytest -v --cov=app --cov-report=term-missing --cov-report=html
```

View HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test Files
```bash
pytest tests/test_api.py -v
```

### Run Specific Test Classes
```bash
pytest tests/test_api.py::TestCreateCustomer -v
```

### Run Specific Test Methods
```bash
pytest tests/test_api.py::TestCreateCustomer::test_create_customer_success -v
```

### Run Tests by Marker
```bash
pytest -m unit  # Run only unit tests
pytest -m api   # Run only API tests
pytest -m messaging  # Run only messaging tests
pytest -m integration  # Run only integration tests
```

## Test Coverage

### Current Test Coverage

**Customer Service:**
- ✅ Create customer (success, duplicate email, missing fields, without phone)
- ✅ Get customers (empty list, multiple customers)
- ✅ Get customer by ID (success, not found, invalid UUID)
- ✅ Update customer (all fields, partial, not found)
- ✅ Delete customer (success, not found)
- ✅ Health check endpoint
- ✅ Customer model (creation, uniqueness, timestamps, queries)

**Notification Service:**
- ✅ Create notification (success, minimal, missing fields, empty customers)
- ✅ Get notifications (empty list, multiple)
- ✅ Get notification by ID (success, not found, invalid UUID)
- ✅ Health check endpoint
- ✅ Notification model (creation, status transitions, timestamps, queries)
- ✅ Message publishing (success, connection failure)

**Email Sender:**
- ✅ Email client (success, failure status codes, exceptions, timeout)
- ✅ Message consumer (success, multiple customers, send failure, malformed messages, partial success)
- ✅ DLQ handler (retry success, retry failure and requeue, max retries exceeded, multiple customers, malformed messages, retry count progression)

### Coverage Goals
- Aim for >80% code coverage across all services
- Focus on critical paths and edge cases
- Mock external dependencies (RabbitMQ, HTTP clients, databases in CI)

## Writing Tests

### Test Fixtures
Fixtures are defined in `conftest.py` files and provide reusable test data and mocks:

**Customer Service:**
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `sample_customer_data`: Sample customer data
- `sample_customer_data_no_phone`: Customer data without phone

**Notification Service:**
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override
- `mock_rabbitmq_channel`: Mocked RabbitMQ channel
- `mock_rabbitmq_connection`: Mocked RabbitMQ connection
- `sample_notification_data`: Sample notification data
- `sample_notification_minimal`: Minimal notification data

**Email Sender:**
- `mock_rabbitmq_channel`: Mocked RabbitMQ channel
- `mock_rabbitmq_connection`: Mocked RabbitMQ connection
- `mock_rabbitmq_message`: Mocked incoming message
- `mock_http_client`: Mocked HTTP client
- `sample_email_request`: Sample email request data
- `sample_email_request_with_retries`: Email request with retries

### Example Test

```python
import pytest

@pytest.mark.api
class TestCreateCustomer:
    """Test cases for creating customers."""

    def test_create_customer_success(self, client, sample_customer_data):
        """Test successful customer creation."""
        response = client.post("/customers/", json=sample_customer_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_customer_data["email"]
        assert "id" in data

    def test_create_customer_duplicate_email(self, client, sample_customer_data):
        """Test that duplicate email addresses are rejected."""
        client.post("/customers/", json=sample_customer_data)
        response = client.post("/customers/", json=sample_customer_data)

        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]
```

### Async Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch("app.services.email_client.httpx.AsyncClient")
async def test_send_email_success(mock_client_class):
    """Test successful email sending."""
    mock_response = AsyncMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    mock_client_class.return_value = mock_client

    result = await send_email("customer-123", "Test", "Body")

    assert result["success"] is True
```

### Test Markers
Use markers to categorize tests:
```python
@pytest.mark.unit         # Unit tests
@pytest.mark.api          # API endpoint tests
@pytest.mark.integration  # Integration tests
@pytest.mark.messaging    # Message queue tests
```

## CI/CD Integration

### GitHub Actions
Tests run automatically on:
- Push to `main` branch
- Pull requests to `main` branch

The CI pipeline:
1. Sets up Python 3.11
2. Starts PostgreSQL and RabbitMQ services
3. Runs tests for each service with coverage
4. Uploads coverage reports to Codecov
5. Builds Docker images (only if tests pass)

### Workflow File
See `.github/workflows/ci.yml` for the complete workflow configuration.

### Environment Variables
The following environment variables are configured in CI:
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `RABBITMQ_EMAIL_QUEUE`: Email queue name
- `RABBITMQ_STATUS_QUEUE`: Status queue name
- `WIREMOCK_URL`: Wiremock endpoint (for email sender)

### Local Testing vs CI
- **Local**: Uses SQLite in-memory database for faster tests
- **CI**: Uses actual PostgreSQL and RabbitMQ services
- Both use mocked RabbitMQ connections where appropriate
- External HTTP calls are always mocked

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use fixtures with proper teardown to clean up resources
3. **Mocking**: Mock external dependencies (RabbitMQ, HTTP clients)
4. **Assertions**: Use clear, specific assertions
5. **Documentation**: Add docstrings to test classes and methods
6. **Coverage**: Aim for high coverage but focus on meaningful tests
7. **Fast Tests**: Keep tests fast by using in-memory databases and mocks
8. **Async**: Use `pytest.mark.asyncio` for async tests

## Troubleshooting

### Tests Failing Locally
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that you're in the correct directory
3. Verify environment variables are set (if needed)

### Import Errors
Add the service directory to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Errors
Tests use SQLite in-memory databases by default, which don't require external services. If you see database errors, check that the fixtures are properly set up.

### Async Test Errors
Ensure `pytest-asyncio` is installed and tests are marked with `@pytest.mark.asyncio`.

## Future Enhancements

- [ ] Add integration tests with real RabbitMQ and PostgreSQL
- [ ] Add load testing with locust or k6
- [ ] Add mutation testing with mutmut
- [ ] Add contract testing for API endpoints
- [ ] Add E2E tests with all services running
- [ ] Set up test data factories with factory_boy
- [ ] Add performance benchmarking tests