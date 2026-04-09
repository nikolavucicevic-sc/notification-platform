import pytest
import logging
from datetime import datetime, timedelta
from uuid import uuid4

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestCreateScheduledNotification:
    """Tests for POST /schedules/"""

    def test_create_one_time_schedule_success(self, client, sample_schedule_data, mock_scheduler):
        """Test creating a one-time scheduled notification."""
        logger.info("Testing one-time schedule creation")
        response = client.post("/schedules", json=sample_schedule_data)
        logger.info(f"Response status: {response.status_code}")

        assert response.status_code == 201
        data = response.json()
        logger.info(f"Created schedule with ID: {data.get('id')}")
        assert data["schedule_type"] == "ONCE"
        assert data["subject"] == sample_schedule_data["subject"]
        assert data["body"] == sample_schedule_data["body"]
        assert data["status"] == "SCHEDULED"
        assert data["is_active"] is True
        assert "id" in data
        assert "job_id" in data
        logger.info("✓ One-time schedule created successfully")

    def test_create_recurring_schedule_success(self, client, sample_recurring_schedule_data, mock_scheduler):
        """Test creating a recurring scheduled notification."""
        response = client.post("/schedules", json=sample_recurring_schedule_data)

        assert response.status_code == 201
        data = response.json()
        assert data["schedule_type"] == "RECURRING"
        assert data["recurrence_type"] == "DAILY"
        assert data["status"] == "SCHEDULED"

    def test_create_recurring_without_recurrence_type_fails(self, client):
        """Test that recurring schedule without recurrence_type fails."""
        schedule_data = {
            "schedule_type": "RECURRING",
            "scheduled_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "notification_type": "EMAIL",
            "subject": "Test",
            "body": "Test body",
            "customer_ids": [str(uuid4())]
        }

        response = client.post("/schedules", json=schedule_data)
        assert response.status_code == 400
        assert "recurrence_type" in response.json()["detail"]

    def test_create_schedule_missing_required_fields(self, client):
        """Test creating schedule with missing required fields fails."""
        incomplete_data = {
            "schedule_type": "ONCE",
            "scheduled_time": datetime.now().isoformat()
        }

        response = client.post("/schedules", json=incomplete_data)
        assert response.status_code == 422


@pytest.mark.api
class TestGetScheduledNotifications:
    """Tests for GET /schedules/"""

    def test_get_all_schedules(self, client, sample_schedule_data, mock_scheduler):
        """Test retrieving all scheduled notifications."""
        # Create two schedules
        client.post("/schedules", json=sample_schedule_data)

        schedule_data_2 = sample_schedule_data.copy()
        schedule_data_2["subject"] = "Second notification"
        client.post("/schedules", json=schedule_data_2)

        # Get all schedules
        response = client.get("/schedules")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_schedules_filtered_by_status(self, client, sample_schedule_data, mock_scheduler):
        """Test filtering schedules by status."""
        client.post("/schedules", json=sample_schedule_data)

        response = client.get("/schedules?status=SCHEDULED")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "SCHEDULED"

    def test_get_schedules_filtered_by_active(self, client, sample_schedule_data, mock_scheduler):
        """Test filtering schedules by is_active flag."""
        response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = response.json()["id"]

        # Pause the schedule
        client.post(f"/schedules/{schedule_id}/pause")

        # Get only active schedules
        response = client.get("/schedules?is_active=true")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Get inactive schedules
        response = client.get("/schedules?is_active=false")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_schedules_pagination(self, client, sample_schedule_data, mock_scheduler):
        """Test pagination with skip and limit."""
        # Create 5 schedules
        for i in range(5):
            data = sample_schedule_data.copy()
            data["subject"] = f"Notification {i}"
            client.post("/schedules", json=data)

        # Get first 2
        response = client.get("/schedules?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Get next 2
        response = client.get("/schedules?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


@pytest.mark.api
class TestGetScheduledNotificationById:
    """Tests for GET /schedules/{schedule_id}"""

    def test_get_schedule_by_id_success(self, client, sample_schedule_data, mock_scheduler):
        """Test retrieving a specific schedule by ID."""
        create_response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = create_response.json()["id"]

        response = client.get(f"/schedules/{schedule_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == schedule_id
        assert data["subject"] == sample_schedule_data["subject"]

    def test_get_schedule_not_found(self, client):
        """Test retrieving non-existent schedule returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/schedules/{fake_id}")
        assert response.status_code == 404


@pytest.mark.api
class TestUpdateScheduledNotification:
    """Tests for PUT /schedules/{schedule_id}"""

    def test_update_schedule_success(self, client, sample_schedule_data, mock_scheduler):
        """Test updating a scheduled notification."""
        create_response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = create_response.json()["id"]

        update_data = {
            "subject": "Updated Subject",
            "body": "Updated body text"
        }

        response = client.put(f"/schedules/{schedule_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Updated Subject"
        assert data["body"] == "Updated body text"

    def test_update_schedule_not_found(self, client):
        """Test updating non-existent schedule returns 404."""
        fake_id = str(uuid4())
        update_data = {"subject": "New subject"}

        response = client.put(f"/schedules/{fake_id}", json=update_data)
        assert response.status_code == 404


@pytest.mark.api
class TestCancelScheduledNotification:
    """Tests for DELETE /schedules/{schedule_id}"""

    def test_cancel_schedule_success(self, client, sample_schedule_data, mock_scheduler):
        """Test canceling a scheduled notification."""
        create_response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = create_response.json()["id"]

        response = client.delete(f"/schedules/{schedule_id}")
        assert response.status_code == 204

        # Verify schedule is cancelled
        get_response = client.get(f"/schedules/{schedule_id}")
        assert get_response.json()["status"] == "CANCELLED"
        assert get_response.json()["is_active"] is False

    def test_cancel_schedule_not_found(self, client):
        """Test canceling non-existent schedule returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/schedules/{fake_id}")
        assert response.status_code == 404


@pytest.mark.api
class TestPauseScheduledNotification:
    """Tests for POST /schedules/{schedule_id}/pause"""

    def test_pause_schedule_success(self, client, sample_schedule_data, mock_scheduler):
        """Test pausing a scheduled notification."""
        create_response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = create_response.json()["id"]

        response = client.post(f"/schedules/{schedule_id}/pause")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_pause_schedule_not_found(self, client):
        """Test pausing non-existent schedule returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/schedules/{fake_id}/pause")
        assert response.status_code == 404


@pytest.mark.api
class TestResumeScheduledNotification:
    """Tests for POST /schedules/{schedule_id}/resume"""

    def test_resume_schedule_success(self, client, sample_schedule_data, mock_scheduler):
        """Test resuming a paused scheduled notification."""
        create_response = client.post("/schedules", json=sample_schedule_data)
        schedule_id = create_response.json()["id"]

        # First pause it
        client.post(f"/schedules/{schedule_id}/pause")

        # Then resume
        response = client.post(f"/schedules/{schedule_id}/resume")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    def test_resume_schedule_not_found(self, client):
        """Test resuming non-existent schedule returns 404."""
        fake_id = str(uuid4())
        response = client.post(f"/schedules/{fake_id}/resume")
        assert response.status_code == 404


@pytest.mark.api
class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.api
class TestRootEndpoint:
    """Tests for / endpoint"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Scheduler Service"
        assert "endpoints" in data
