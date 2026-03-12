from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.models.notification import NotificationType, NotificationStatus


class NotificationCreate(BaseModel):
    notification_type: NotificationType
    subject: str
    body: str
    customer_ids: list[UUID]


class NotificationResponse(BaseModel):
    id: UUID
    notification_type: NotificationType
    subject: str
    body: str
    customer_ids: list[str]
    status: NotificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True