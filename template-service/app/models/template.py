from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()


class ChannelType(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    channel_type = Column(SQLEnum(ChannelType), nullable=False, default=ChannelType.EMAIL)

    # For EMAIL templates
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)

    # Variables: stored as comma-separated string (e.g., "first_name,last_name,email")
    variables = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Template {self.name} ({self.channel_type})>"
