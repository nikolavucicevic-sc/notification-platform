from sqlalchemy import Column, String, DateTime, Enum, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum

from app.database import Base


class UserRole(enum.Enum):
    ADMIN = "ADMIN"  # Full access: manage users, send notifications, view everything
    OPERATOR = "OPERATOR"  # Send notifications, view monitoring, retry failed messages
    VIEWER = "VIEWER"  # Read-only access


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Sending limits (None = unlimited)
    email_limit = Column(Integer, nullable=True, default=None)
    sms_limit = Column(Integer, nullable=True, default=None)

    # Running counters
    email_sent = Column(Integer, nullable=False, default=0)
    sms_sent = Column(Integer, nullable=False, default=0)
