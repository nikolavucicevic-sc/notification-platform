from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.tenant import PlanTier


class TenantCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    reply_to_email: Optional[EmailStr] = None
    email_limit: Optional[int] = Field(None, ge=0)
    sms_limit: Optional[int] = Field(None, ge=0)
    # First admin account for the tenant
    admin_username: str
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    admin_full_name: Optional[str] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    reply_to_email: Optional[EmailStr] = None
    email_limit: Optional[int] = Field(None, ge=0)
    sms_limit: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    display_name: Optional[str] = None
    reply_to_email: Optional[str] = None
    email_limit: Optional[int]
    sms_limit: Optional[int]
    email_sent: int
    sms_sent: int
    is_active: bool
    plan: PlanTier = PlanTier.FREE
    created_at: datetime
    user_count: Optional[int] = None

    class Config:
        from_attributes = True
