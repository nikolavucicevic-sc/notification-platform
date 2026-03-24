from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ScheduledNotificationCreate(BaseModel):
    """Schema for creating a scheduled notification"""
    schedule_type: str = Field(..., description="ONCE or RECURRING")
    scheduled_time: datetime = Field(..., description="When to send the notification")

    # Optional recurrence
    recurrence_type: Optional[str] = Field(None, description="HOURLY, DAILY, WEEKLY, or MONTHLY")
    recurrence_end_date: Optional[datetime] = Field(None, description="When to stop recurring")

    # Notification content
    notification_type: str = Field(default="EMAIL", description="Type of notification")
    subject: str = Field(..., min_length=1, description="Notification subject")
    body: str = Field(..., min_length=1, description="Notification body")
    customer_ids: List[UUID] = Field(..., min_items=1, description="List of customer IDs")

    # Optional metadata
    created_by: Optional[str] = Field(None, description="User who created the schedule")


class ScheduledNotificationUpdate(BaseModel):
    """Schema for updating a scheduled notification"""
    scheduled_time: Optional[datetime] = None
    recurrence_end_date: Optional[datetime] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    customer_ids: Optional[List[UUID]] = None
    is_active: Optional[bool] = None


class ScheduledNotificationResponse(BaseModel):
    """Schema for scheduled notification response"""
    id: UUID
    schedule_type: str
    scheduled_time: datetime
    recurrence_type: Optional[str]
    recurrence_end_date: Optional[datetime]

    notification_type: str
    subject: str
    body: str
    customer_ids: List[str]

    status: str
    job_id: Optional[str]

    last_run: Optional[datetime]
    next_run: Optional[datetime]
    run_count: str

    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True
