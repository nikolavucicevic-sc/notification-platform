from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum

from app.database import Base


class PlanTier(str, enum.Enum):
    FREE = "FREE"           # 1k emails/mo, 500 SMS
    PRO = "PRO"             # 50k emails/mo, 10k SMS
    BUSINESS = "BUSINESS"   # Unlimited


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)        # e.g. "Acme Notifications" — shown in From header
    reply_to_email = Column(String, nullable=True)      # e.g. "support@acme.com" — Reply-To header
    email_limit = Column(Integer, nullable=True, default=None)   # None = unlimited
    sms_limit = Column(Integer, nullable=True, default=None)
    email_sent = Column(Integer, nullable=False, default=0)
    sms_sent = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    # Billing
    plan = Column(SAEnum(PlanTier), nullable=False, default=PlanTier.FREE)
    stripe_customer_id = Column(String, nullable=True, unique=True)
    stripe_subscription_id = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
