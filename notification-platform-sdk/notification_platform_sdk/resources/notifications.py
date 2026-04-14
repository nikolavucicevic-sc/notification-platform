"""
Notifications API resource.
"""

from typing import List, Optional, Dict, Any


class NotificationsResource:
    """Handles notification-related API operations."""

    def __init__(self, client):
        """
        Initialize the notifications resource.

        Args:
            client: BaseClient instance
        """
        self._client = client

    def send(
        self,
        customer_id: str,
        channel: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[str] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a notification to a customer.

        Args:
            customer_id: The customer's unique identifier
            channel: Notification channel ("email", "sms", or "push")
            subject: Notification subject (required for email, optional for others)
            body: Notification body (required if not using template)
            template_id: Template ID to use (optional, alternative to body)
            template_data: Data to render template with (required if template_id is provided)
            scheduled_at: ISO 8601 timestamp to schedule notification (optional)
            priority: Priority level ("low", "normal", "high") (default: "normal")
            metadata: Additional metadata (optional)

        Returns:
            Created notification object

        Example:
            >>> # Send an email notification
            >>> notification = client.notifications.send(
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     channel="email",
            ...     subject="Welcome!",
            ...     body="Welcome to our platform!",
            ...     priority="high"
            ... )

            >>> # Send SMS with template
            >>> notification = client.notifications.send(
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     channel="sms",
            ...     template_id="welcome_sms",
            ...     template_data={"name": "John"}
            ... )

            >>> # Schedule a notification
            >>> notification = client.notifications.send(
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     channel="email",
            ...     subject="Reminder",
            ...     body="Don't forget!",
            ...     scheduled_at="2024-12-25T10:00:00Z"
            ... )
        """
        data = {
            "customer_id": customer_id,
            "channel": channel,
            "priority": priority,
        }

        if subject is not None:
            data["subject"] = subject
        if body is not None:
            data["body"] = body
        if template_id is not None:
            data["template_id"] = template_id
        if template_data is not None:
            data["template_data"] = template_data
        if scheduled_at is not None:
            data["scheduled_at"] = scheduled_at
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.post("/api/notifications/", json=data)

    def list(
        self,
        customer_id: Optional[str] = None,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List notifications with optional filtering.

        Args:
            customer_id: Filter by customer ID (optional)
            channel: Filter by channel (optional)
            status: Filter by status (optional)
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of notification objects

        Example:
            >>> # Get all notifications
            >>> notifications = client.notifications.list()

            >>> # Get notifications for specific customer
            >>> notifications = client.notifications.list(
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000"
            ... )

            >>> # Get failed email notifications
            >>> notifications = client.notifications.list(
            ...     channel="email",
            ...     status="failed"
            ... )
        """
        params = {"skip": skip, "limit": limit}
        if customer_id is not None:
            params["customer_id"] = customer_id
        if channel is not None:
            params["channel"] = channel
        if status is not None:
            params["status"] = status

        return self._client.get("/api/notifications/", params=params)

    def get(self, notification_id: str) -> Dict[str, Any]:
        """
        Get a specific notification by ID.

        Args:
            notification_id: The notification's unique identifier

        Returns:
            Notification object

        Example:
            >>> notification = client.notifications.get("123e4567-e89b-12d3-a456-426614174000")
            >>> print(notification["status"])
        """
        return self._client.get(f"/api/notifications/{notification_id}")

    def update_status(
        self,
        notification_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a notification's status.

        Args:
            notification_id: The notification's unique identifier
            status: New status ("pending", "sent", "delivered", "failed", "cancelled")
            error_message: Error message if status is "failed" (optional)

        Returns:
            Updated notification object

        Example:
            >>> notification = client.notifications.update_status(
            ...     "123e4567-e89b-12d3-a456-426614174000",
            ...     status="delivered"
            ... )

            >>> # Mark as failed with error
            >>> notification = client.notifications.update_status(
            ...     "123e4567-e89b-12d3-a456-426614174000",
            ...     status="failed",
            ...     error_message="Recipient email bounced"
            ... )
        """
        data = {"status": status}
        if error_message is not None:
            data["error_message"] = error_message

        return self._client.patch(f"/api/notifications/{notification_id}/status", json=data)

    def retry(self, notification_id: str) -> Dict[str, Any]:
        """
        Retry a failed notification.

        Args:
            notification_id: The notification's unique identifier

        Returns:
            Updated notification object

        Example:
            >>> notification = client.notifications.retry("123e4567-e89b-12d3-a456-426614174000")
        """
        return self._client.post(f"/api/notifications/{notification_id}/retry")

    def cancel(self, notification_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled notification.

        Args:
            notification_id: The notification's unique identifier

        Returns:
            Updated notification object

        Example:
            >>> notification = client.notifications.cancel("123e4567-e89b-12d3-a456-426614174000")
        """
        return self._client.post(f"/api/notifications/{notification_id}/cancel")

    def get_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get notification statistics.

        Args:
            start_date: Start date in ISO 8601 format (optional)
            end_date: End date in ISO 8601 format (optional)

        Returns:
            Statistics object with counts by status and channel

        Example:
            >>> stats = client.notifications.get_stats(
            ...     start_date="2024-01-01T00:00:00Z",
            ...     end_date="2024-12-31T23:59:59Z"
            ... )
            >>> print(stats)
        """
        params = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date

        return self._client.get("/api/notifications/stats", params=params)
