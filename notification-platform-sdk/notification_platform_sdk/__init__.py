"""
Notification Platform SDK

A Python client library for the Notification Platform API.
"""

from .client import NotificationPlatformClient
from .exceptions import (
    NotificationPlatformError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "NotificationPlatformClient",
    "NotificationPlatformError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
]
