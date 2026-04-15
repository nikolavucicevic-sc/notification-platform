from pydantic import BaseModel, model_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.models.notification import NotificationType, NotificationStatus


class NotificationCreate(BaseModel):
    notification_type: NotificationType
    subject: Optional[str] = None  # Required for EMAIL unless template_id provided
    body: Optional[str] = None     # Required unless template_id provided
    customer_ids: list[UUID]
    template_id: Optional[str] = None          # UUID of a template in template-service
    template_variables: Optional[dict] = None  # Variables to render the template with

    @model_validator(mode='after')
    def validate_body_or_template(self):
        if not self.template_id and not self.body:
            raise ValueError('Either body or template_id must be provided')
        if self.notification_type == NotificationType.EMAIL and not self.template_id and not self.subject:
            raise ValueError('Subject is required for EMAIL notifications when not using a template')
        return self


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