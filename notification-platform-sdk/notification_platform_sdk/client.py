"""
Main client for the Notification Platform SDK.
"""

from .base_client import BaseClient
from .resources import (
    CustomersResource,
    NotificationsResource,
    TemplatesResource,
    SchedulesResource,
)


class NotificationPlatformClient:
    """
    Main client for interacting with the Notification Platform API.

    This client provides access to all API resources through convenient properties.

    Example:
        >>> from notification_platform_sdk import NotificationPlatformClient
        >>>
        >>> # Initialize the client
        >>> client = NotificationPlatformClient(
        ...     base_url="https://api.example.com",
        ...     api_key="your-api-key-here"
        ... )
        >>>
        >>> # Create a customer
        >>> customer = client.customers.create(
        ...     email="john@example.com",
        ...     first_name="John",
        ...     last_name="Doe"
        ... )
        >>>
        >>> # Send a notification
        >>> notification = client.notifications.send(
        ...     customer_id=customer["id"],
        ...     channel="email",
        ...     subject="Welcome!",
        ...     body="Welcome to our platform!"
        ... )
        >>>
        >>> # Use as context manager
        >>> with NotificationPlatformClient(base_url="...", api_key="...") as client:
        ...     customers = client.customers.list()
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Initialize the Notification Platform client.

        Args:
            base_url: The base URL of the API (e.g., "https://api.example.com")
            api_key: Your API key for authentication
            timeout: Request timeout in seconds (default: 30)

        Example:
            >>> client = NotificationPlatformClient(
            ...     base_url="https://notifications.example.com",
            ...     api_key="np_1234567890abcdef"
            ... )
        """
        self._base_client = BaseClient(base_url, api_key, timeout)

        # Initialize resource clients
        self._customers = CustomersResource(self._base_client)
        self._notifications = NotificationsResource(self._base_client)
        self._templates = TemplatesResource(self._base_client)
        self._schedules = SchedulesResource(self._base_client)

    @property
    def customers(self) -> CustomersResource:
        """
        Access the Customers API.

        Returns:
            CustomersResource instance for customer operations

        Example:
            >>> customer = client.customers.create(email="john@example.com")
            >>> customers = client.customers.list()
            >>> customer = client.customers.get(customer_id)
            >>> client.customers.delete(customer_id)
        """
        return self._customers

    @property
    def notifications(self) -> NotificationsResource:
        """
        Access the Notifications API.

        Returns:
            NotificationsResource instance for notification operations

        Example:
            >>> notification = client.notifications.send(
            ...     customer_id="...",
            ...     channel="email",
            ...     subject="Hello",
            ...     body="World"
            ... )
            >>> notifications = client.notifications.list()
            >>> notification = client.notifications.get(notification_id)
        """
        return self._notifications

    @property
    def templates(self) -> TemplatesResource:
        """
        Access the Templates API.

        Returns:
            TemplatesResource instance for template operations

        Example:
            >>> template = client.templates.create(
            ...     name="welcome",
            ...     channel="email",
            ...     subject="Welcome {{name}}!",
            ...     body_template="Hi {{name}}, welcome!"
            ... )
            >>> templates = client.templates.list()
            >>> template = client.templates.get(template_id)
        """
        return self._templates

    @property
    def schedules(self) -> SchedulesResource:
        """
        Access the Schedules API.

        Returns:
            SchedulesResource instance for schedule operations

        Example:
            >>> schedule = client.schedules.create(
            ...     name="Daily reminder",
            ...     customer_id="...",
            ...     channel="email",
            ...     cron_expression="0 9 * * *",
            ...     subject="Daily Reminder",
            ...     body="Don't forget!"
            ... )
            >>> schedules = client.schedules.list()
            >>> schedule = client.schedules.get(schedule_id)
        """
        return self._schedules

    def close(self):
        """
        Close the client and clean up resources.

        Example:
            >>> client = NotificationPlatformClient(base_url="...", api_key="...")
            >>> # ... use client ...
            >>> client.close()
        """
        self._base_client.close()

    def __enter__(self):
        """
        Context manager entry.

        Example:
            >>> with NotificationPlatformClient(base_url="...", api_key="...") as client:
            ...     customers = client.customers.list()
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self):
        """String representation of the client."""
        return f"NotificationPlatformClient(base_url='{self._base_client.base_url}')"
