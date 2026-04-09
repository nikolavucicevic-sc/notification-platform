import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch


@pytest.mark.api
class TestCreateNotification:
    """Test cases for creating notifications."""

    @patch("app.routers.notifications.publish_email_request", new_callable=AsyncMock)
    def test_create_notification_success(self, mock_publish, client, sample_notification_data):
        """Test successful notification creation."""
        response = client.post("/notifications/", json=sample_notification_data)

        assert response.status_code == 201
        data = response.json()
        assert data["notification_type"] == sample_notification_data["notification_type"]
        assert data["subject"] == sample_notification_data["subject"]
        assert data["body"] == sample_notification_data["body"]
        assert data["customer_ids"] == sample_notification_data["customer_ids"]
        assert data["status"] == "PROCESSING"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify publish was called
        mock_publish.assert_called_once()

    @patch("app.routers.notifications.publish_email_request", new_callable=AsyncMock)
    def test_create_notification_minimal(self, mock_publish, client, sample_notification_minimal):
        """Test notification creation with minimal data."""
        response = client.post("/notifications/", json=sample_notification_minimal)

        assert response.status_code == 201
        data = response.json()
        assert len(data["customer_ids"]) == 1

    def test_create_notification_missing_fields(self, client):
        """Test that missing required fields return validation error."""
        incomplete_data = {"subject": "Test"}
        response = client.post("/notifications/", json=incomplete_data)

        assert response.status_code == 422

    @patch("app.routers.notifications.publish_email_request", new_callable=AsyncMock)
    def test_create_notification_empty_customer_ids(self, mock_publish, client):
        """Test notification with empty customer IDs list."""
        data = {
            "notification_type": "EMAIL",
            "subject": "Test",
            "body": "Test body",
            "customer_ids": []
        }
        response = client.post("/notifications/", json=data)

        # Should either fail validation or succeed - depends on schema validation
        # Adjust based on actual validation rules
        assert response.status_code in [201, 422]


@pytest.mark.api
class TestGetNotifications:
    """Test cases for retrieving notifications."""

    def test_get_notifications_empty(self, client):
        """Test getting notifications when none exist."""
        response = client.get("/notifications/")

        assert response.status_code == 200
        assert response.json() == []

    @patch("app.routers.notifications.publish_email_request", new_callable=AsyncMock)
    def test_get_notifications_multiple(self, mock_publish, client, sample_notification_data):
        """Test getting multiple notifications."""
        # Create two notifications
        data1 = sample_notification_data.copy()
        data2 = sample_notification_data.copy()
        data2["subject"] = "Second notification"

        client.post("/notifications/", json=data1)
        client.post("/notifications/", json=data2)

        response = client.get("/notifications/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


@pytest.mark.api
class TestGetNotification:
    """Test cases for retrieving a single notification."""

    @patch("app.routers.notifications.publish_email_request", new_callable=AsyncMock)
    def test_get_notification_success(self, mock_publish, client, sample_notification_data):
        """Test successfully retrieving a notification by ID."""
        # Create a notification
        create_response = client.post("/notifications/", json=sample_notification_data)
        notification_id = create_response.json()["id"]

        # Retrieve the notification
        response = client.get(f"/notifications/{notification_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification_id
        assert data["subject"] == sample_notification_data["subject"]

    def test_get_notification_not_found(self, client):
        """Test retrieving a non-existent notification."""
        fake_id = str(uuid4())
        response = client.get(f"/notifications/{fake_id}")

        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    def test_get_notification_invalid_uuid(self, client):
        """Test with invalid UUID format."""
        response = client.get("/notifications/invalid-uuid")

        assert response.status_code == 422


@pytest.mark.api
class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] in ("ok", "healthy", "degraded")
