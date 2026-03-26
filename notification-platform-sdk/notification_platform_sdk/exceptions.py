"""
Custom exceptions for the Notification Platform SDK.
"""


class NotificationPlatformError(Exception):
    """Base exception for all Notification Platform errors."""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(NotificationPlatformError):
    """Raised when authentication fails (401 Unauthorized)."""
    pass


class NotFoundError(NotificationPlatformError):
    """Raised when a resource is not found (404 Not Found)."""
    pass


class ValidationError(NotificationPlatformError):
    """Raised when request validation fails (400 Bad Request, 422 Unprocessable Entity)."""
    pass


class RateLimitError(NotificationPlatformError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""
    pass


class ForbiddenError(NotificationPlatformError):
    """Raised when access is forbidden (403 Forbidden)."""
    pass


class ServerError(NotificationPlatformError):
    """Raised when server encounters an error (5xx)."""
    pass
