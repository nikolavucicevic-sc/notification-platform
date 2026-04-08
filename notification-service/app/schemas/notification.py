from pydantic import BaseModel, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.models.notification import NotificationType, NotificationStatus


class NotificationCreate(BaseModel):
    notification_type: NotificationType
    subject: Optional[str] = None  # Optional - required for EMAIL, not used for SMS
    body: str
    customer_ids: list[UUID]

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v, info):
        # Subject is required for EMAIL but not for SMS
        notification_type = info.data.get('notification_type')
        if notification_type == NotificationType.EMAIL and not v:
            raise ValueError('Subject is required for EMAIL notifications')
        return v


class NotificationResponse(BaseModel):
    id: UUID
    notification_type: NotificationType
    subject: Optional[str] = None
    body: str
    customer_ids: list[str]
    status: NotificationStatus
    created_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True