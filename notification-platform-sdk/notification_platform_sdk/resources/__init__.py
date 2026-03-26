"""
API resources for the Notification Platform SDK.
"""

from .customers import CustomersResource
from .notifications import NotificationsResource
from .templates import TemplatesResource
from .schedules import SchedulesResource

__all__ = [
    "CustomersResource",
    "NotificationsResource",
    "TemplatesResource",
    "SchedulesResource",
]
