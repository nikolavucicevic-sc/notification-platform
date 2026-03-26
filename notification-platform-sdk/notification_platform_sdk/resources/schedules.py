"""
Schedules API resource.
"""

from typing import List, Optional, Dict, Any


class SchedulesResource:
    """Handles schedule-related API operations."""

    def __init__(self, client):
        """
        Initialize the schedules resource.

        Args:
            client: BaseClient instance
        """
        self._client = client

    def create(
        self,
        name: str,
        customer_id: str,
        channel: str,
        cron_expression: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        timezone: str = "UTC",
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new recurring notification schedule.

        Args:
            name: Schedule name/description
            customer_id: The customer's unique identifier
            channel: Notification channel ("email", "sms", or "push")
            cron_expression: Cron expression for schedule (e.g., "0 9 * * MON")
            template_id: Template ID to use (optional)
            template_data: Data to render template with (optional)
            subject: Notification subject (for email)
            body: Notification body (if not using template)
            timezone: Timezone for schedule (default: "UTC")
            enabled: Whether schedule is active (default: True)
            metadata: Additional metadata (optional)

        Returns:
            Created schedule object

        Example:
            >>> # Daily reminder at 9 AM
            >>> schedule = client.schedules.create(
            ...     name="Daily reminder",
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     channel="email",
            ...     cron_expression="0 9 * * *",
            ...     subject="Daily Reminder",
            ...     body="Don't forget to check your tasks!",
            ...     timezone="America/New_York"
            ... )

            >>> # Weekly report on Mondays at 10 AM
            >>> schedule = client.schedules.create(
            ...     name="Weekly report",
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     channel="email",
            ...     cron_expression="0 10 * * MON",
            ...     template_id="weekly_report",
            ...     template_data={"report_type": "sales"},
            ...     timezone="UTC"
            ... )
        """
        data = {
            "name": name,
            "customer_id": customer_id,
            "channel": channel,
            "cron_expression": cron_expression,
            "timezone": timezone,
            "enabled": enabled,
        }

        if template_id is not None:
            data["template_id"] = template_id
        if template_data is not None:
            data["template_data"] = template_data
        if subject is not None:
            data["subject"] = subject
        if body is not None:
            data["body"] = body
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.post("/api/schedules/", json=data)

    def list(
        self,
        customer_id: Optional[str] = None,
        enabled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List schedules with optional filtering.

        Args:
            customer_id: Filter by customer ID (optional)
            enabled: Filter by enabled status (optional)
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of schedule objects

        Example:
            >>> # Get all schedules
            >>> schedules = client.schedules.list()

            >>> # Get active schedules for customer
            >>> schedules = client.schedules.list(
            ...     customer_id="123e4567-e89b-12d3-a456-426614174000",
            ...     enabled=True
            ... )
        """
        params = {"skip": skip, "limit": limit}
        if customer_id is not None:
            params["customer_id"] = customer_id
        if enabled is not None:
            params["enabled"] = enabled

        return self._client.get("/api/schedules/", params=params)

    def get(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get a specific schedule by ID.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            Schedule object

        Example:
            >>> schedule = client.schedules.get("123e4567-e89b-12d3-a456-426614174000")
            >>> print(schedule["cron_expression"])
        """
        return self._client.get(f"/api/schedules/{schedule_id}")

    def update(
        self,
        schedule_id: str,
        name: Optional[str] = None,
        cron_expression: Optional[str] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        timezone: Optional[str] = None,
        enabled: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a schedule.

        Args:
            schedule_id: The schedule's unique identifier
            name: New schedule name (optional)
            cron_expression: New cron expression (optional)
            template_id: New template ID (optional)
            template_data: New template data (optional)
            subject: New subject (optional)
            body: New body (optional)
            timezone: New timezone (optional)
            enabled: Enable/disable schedule (optional)
            metadata: New metadata (optional)

        Returns:
            Updated schedule object

        Example:
            >>> # Disable a schedule
            >>> schedule = client.schedules.update(
            ...     "123e4567-e89b-12d3-a456-426614174000",
            ...     enabled=False
            ... )

            >>> # Change schedule time
            >>> schedule = client.schedules.update(
            ...     "123e4567-e89b-12d3-a456-426614174000",
            ...     cron_expression="0 10 * * *"  # Change to 10 AM
            ... )
        """
        data = {}
        if name is not None:
            data["name"] = name
        if cron_expression is not None:
            data["cron_expression"] = cron_expression
        if template_id is not None:
            data["template_id"] = template_id
        if template_data is not None:
            data["template_data"] = template_data
        if subject is not None:
            data["subject"] = subject
        if body is not None:
            data["body"] = body
        if timezone is not None:
            data["timezone"] = timezone
        if enabled is not None:
            data["enabled"] = enabled
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.put(f"/api/schedules/{schedule_id}", json=data)

    def delete(self, schedule_id: str) -> None:
        """
        Delete a schedule.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            None

        Example:
            >>> client.schedules.delete("123e4567-e89b-12d3-a456-426614174000")
        """
        return self._client.delete(f"/api/schedules/{schedule_id}")

    def enable(self, schedule_id: str) -> Dict[str, Any]:
        """
        Enable a schedule.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            Updated schedule object

        Example:
            >>> schedule = client.schedules.enable("123e4567-e89b-12d3-a456-426614174000")
        """
        return self.update(schedule_id, enabled=True)

    def disable(self, schedule_id: str) -> Dict[str, Any]:
        """
        Disable a schedule.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            Updated schedule object

        Example:
            >>> schedule = client.schedules.disable("123e4567-e89b-12d3-a456-426614174000")
        """
        return self.update(schedule_id, enabled=False)

    def get_next_run(self, schedule_id: str) -> Dict[str, str]:
        """
        Get the next scheduled run time for a schedule.

        Args:
            schedule_id: The schedule's unique identifier

        Returns:
            Object with "next_run" timestamp

        Example:
            >>> next_run = client.schedules.get_next_run("123e4567-e89b-12d3-a456-426614174000")
            >>> print(next_run["next_run"])  # "2024-12-25T10:00:00Z"
        """
        return self._client.get(f"/api/schedules/{schedule_id}/next-run")
