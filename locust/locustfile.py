"""
Locust load testing suite for Notification Platform.

Scenarios:
1. Normal load: Steady traffic simulating typical usage
2. Spike test: Sudden burst of traffic
3. Stress test: Gradually increasing load to find breaking point

Usage:
    # Start Locust web UI
    locust -f locustfile.py --host=http://localhost:8002

    # Headless mode (10 users, spawn rate 1/sec, run for 60s)
    locust -f locustfile.py --host=http://localhost:8002 --users 10 --spawn-rate 1 --run-time 60s --headless
"""
from locust import HttpUser, task, between, events
import json
import random


class NotificationPlatformUser(HttpUser):
    """
    Simulates a user of the notification platform.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """
        Called when a simulated user starts.
        Login and get auth token.
        """
        # Login as admin (you need to create this user first)
        response = self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ User logged in successfully")
        else:
            print(f"❌ Login failed: {response.text}")
            self.token = None
            self.headers = {}

    @task(5)  # Weight 5 - most common operation
    def create_email_notification(self):
        """
        Create an email notification.
        """
        if not self.token:
            return

        payload = {
            "notification_type": "EMAIL",
            "subject": f"Load Test Email {random.randint(1000, 9999)}",
            "body": "This is a test email from Locust load testing.",
            "customer_ids": [str(random.randint(1, 100))]
        }

        with self.client.post(
            "/notifications/",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 429:
                # Rate limited - expected behavior
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(3)  # Weight 3
    def create_sms_notification(self):
        """
        Create an SMS notification.
        """
        if not self.token:
            return

        payload = {
            "notification_type": "SMS",
            "body": f"Test SMS {random.randint(1000, 9999)}",
            "customer_ids": [str(random.randint(1, 100))]
        }

        with self.client.post(
            "/notifications/",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 429:
                # Rate limited - expected behavior
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(2)  # Weight 2
    def list_notifications(self):
        """
        List all notifications.
        """
        if not self.token:
            return

        with self.client.get(
            "/notifications/",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

    @task(1)  # Weight 1
    def check_health(self):
        """
        Check health endpoint (doesn't require auth).
        """
        with self.client.get("/health/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(1)  # Weight 1
    def check_dlq(self):
        """
        Check dead letter queue.
        """
        if not self.token:
            return

        with self.client.get(
            "/dlq/",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"DLQ check failed: {response.status_code}")


class ReadOnlyUser(HttpUser):
    """
    Simulates a read-only user (Viewer role).
    Only performs GET requests.
    """
    wait_time = between(2, 5)

    def on_start(self):
        """Login as viewer."""
        # Note: You need to create a viewer user first
        response = self.client.post("/auth/login", json={
            "username": "viewer",
            "password": "viewer123"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task
    def list_notifications(self):
        """List notifications."""
        if not self.token:
            return

        self.client.get("/notifications/", headers=self.headers)

    @task
    def check_health(self):
        """Check health."""
        self.client.get("/health/")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test starts.
    """
    print("=" * 80)
    print("🚀 Starting Locust load test for Notification Platform")
    print("=" * 80)
    print()
    print("Test scenarios:")
    print("  • Creating email notifications (weight: 5)")
    print("  • Creating SMS notifications (weight: 3)")
    print("  • Listing notifications (weight: 2)")
    print("  • Health checks (weight: 1)")
    print("  • DLQ checks (weight: 1)")
    print()
    print("Prerequisites:")
    print("  1. Admin user must exist (username: admin, password: admin123)")
    print("  2. Run: docker exec notification-service python create_admin.py")
    print()
    print("=" * 80)
    print()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test stops.
    """
    print()
    print("=" * 80)
    print("✅ Load test completed!")
    print("=" * 80)
    print()
    print("View detailed results at http://localhost:8089")
    print()
