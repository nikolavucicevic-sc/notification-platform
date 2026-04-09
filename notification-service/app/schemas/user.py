from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models import UserRole


# Request schemas
class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserLimitsUpdate(BaseModel):
    email_limit: Optional[int] = Field(None, ge=0)
    sms_limit: Optional[int] = Field(None, ge=0)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)


# Response schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    tenant_id: Optional[UUID]
    email_limit: Optional[int]
    sms_limit: Optional[int]
    email_sent: int
    sms_sent: int

    class Config:
        from_attributes = True


class UserUsageResponse(BaseModel):
    email_limit: Optional[int]
    sms_limit: Optional[int]
    email_sent: int
    sms_sent: int
    email_remaining: Optional[int]
    sms_remaining: Optional[int]

    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    key_name: str
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    id: UUID
    key_name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    api_key: str
    key_info: APIKeyResponse


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
