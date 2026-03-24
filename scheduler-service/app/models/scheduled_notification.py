from sqlalchemy import Column, String, DateTime, Enum, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum

from app.database import Base


class ScheduleType(enum.Enum):
    ONCE = "ONCE"
    RECURRING = "RECURRING"


class RecurrenceType(enum.Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class JobStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ScheduledNotification(Base):
    __tablename__ = "scheduled_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Schedule details
    schedule_type = Column(Enum(ScheduleType), nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)

    # Recurrence details (optional)
    recurrence_type = Column(Enum(RecurrenceType), nullable=True)
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)

    # Notification details
    notification_type = Column(String, nullable=False, default="EMAIL")
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    customer_ids = Column(JSON, nullable=False)

    # Job status
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.SCHEDULED)
    job_id = Column(String, nullable=True)  # APScheduler job ID

    # Execution tracking
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    run_count = Column(String, nullable=False, default="0")

    # Flags
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(String, nullable=True)
