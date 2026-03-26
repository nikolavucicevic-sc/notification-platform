"""
Templates API resource.
"""

from typing import List, Optional, Dict, Any


class TemplatesResource:
    """Handles template-related API operations."""

    def __init__(self, client):
        """
        Initialize the templates resource.

        Args:
            client: BaseClient instance
        """
        self._client = client

    def create(
        self,
        name: str,
        channel: str,
        subject: Optional[str] = None,
        body_template: Optional[str] = None,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new notification template.

        Args:
            name: Template name (unique identifier)
            channel: Notification channel ("email", "sms", or "push")
            subject: Subject template (required for email, optional for others)
            body_template: Body template with {{variable}} placeholders
            variables: List of variable names used in template (optional)
            metadata: Additional metadata (optional)

        Returns:
            Created template object

        Example:
            >>> # Email template
            >>> template = client.templates.create(
            ...     name="welcome_email",
            ...     channel="email",
            ...     subject="Welcome {{name}}!",
            ...     body_template="Hi {{name}}, welcome to {{company}}!",
            ...     variables=["name", "company"]
            ... )

            >>> # SMS template
            >>> template = client.templates.create(
            ...     name="otp_sms",
            ...     channel="sms",
            ...     body_template="Your OTP is {{code}}. Valid for {{minutes}} minutes.",
            ...     variables=["code", "minutes"]
            ... )
        """
        data = {
            "name": name,
            "channel": channel,
        }

        if subject is not None:
            data["subject"] = subject
        if body_template is not None:
            data["body_template"] = body_template
        if variables is not None:
            data["variables"] = variables
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.post("/api/templates/", json=data)

    def list(
        self,
        channel: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List templates with optional filtering.

        Args:
            channel: Filter by channel (optional)
            skip: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of template objects

        Example:
            >>> # Get all templates
            >>> templates = client.templates.list()

            >>> # Get email templates only
            >>> templates = client.templates.list(channel="email")
        """
        params = {"skip": skip, "limit": limit}
        if channel is not None:
            params["channel"] = channel

        return self._client.get("/api/templates/", params=params)

    def get(self, template_id: str) -> Dict[str, Any]:
        """
        Get a specific template by ID.

        Args:
            template_id: The template's unique identifier (name or UUID)

        Returns:
            Template object

        Example:
            >>> template = client.templates.get("welcome_email")
            >>> print(template["body_template"])
        """
        return self._client.get(f"/api/templates/{template_id}")

    def update(
        self,
        template_id: str,
        name: Optional[str] = None,
        subject: Optional[str] = None,
        body_template: Optional[str] = None,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a template.

        Args:
            template_id: The template's unique identifier
            name: New template name (optional)
            subject: New subject template (optional)
            body_template: New body template (optional)
            variables: New list of variables (optional)
            metadata: New metadata (optional)

        Returns:
            Updated template object

        Example:
            >>> template = client.templates.update(
            ...     "welcome_email",
            ...     subject="Welcome {{name}} to {{company}}!",
            ...     body_template="Hi {{name}}, thanks for joining {{company}}!"
            ... )
        """
        data = {}
        if name is not None:
            data["name"] = name
        if subject is not None:
            data["subject"] = subject
        if body_template is not None:
            data["body_template"] = body_template
        if variables is not None:
            data["variables"] = variables
        if metadata is not None:
            data["metadata"] = metadata

        return self._client.put(f"/api/templates/{template_id}", json=data)

    def delete(self, template_id: str) -> None:
        """
        Delete a template.

        Args:
            template_id: The template's unique identifier

        Returns:
            None

        Example:
            >>> client.templates.delete("old_template")
        """
        return self._client.delete(f"/api/templates/{template_id}")

    def render(
        self,
        template_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Preview/render a template with data (without sending).

        Args:
            template_id: The template's unique identifier
            data: Data to render template with

        Returns:
            Rendered template with "subject" and "body" keys

        Example:
            >>> rendered = client.templates.render(
            ...     "welcome_email",
            ...     data={"name": "John", "company": "Acme Corp"}
            ... )
            >>> print(rendered["subject"])  # "Welcome John!"
            >>> print(rendered["body"])     # "Hi John, welcome to Acme Corp!"
        """
        return self._client.post(f"/api/templates/{template_id}/render", json=data)
