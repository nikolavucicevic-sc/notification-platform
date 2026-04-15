from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID
import re
import bleach

# E.164 international format: + followed by 7-15 digits
E164_PATTERN = r"^\+[1-9]\d{6,14}$"


class CustomerCreate(BaseModel):
    email: EmailStr
    phone_number: str | None = Field(
        None,
        pattern=E164_PATTERN,
        description="Phone number in E.164 format (e.g., +38164123456, +14155552671)"
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        if v:
            cleaned = bleach.clean(v, tags=[], strip=True)
            cleaned = " ".join(cleaned.split())
            return cleaned
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(E164_PATTERN, v):
            raise ValueError("Phone number must be in E.164 format (e.g., +38164123456)")
        return v


class CustomerUpdate(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = Field(
        None,
        pattern=E164_PATTERN,
        description="Phone number in E.164 format (e.g., +38164123456, +14155552671)"
    )
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)

    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        if v:
            cleaned = bleach.clean(v, tags=[], strip=True)
            cleaned = " ".join(cleaned.split())
            return cleaned
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(E164_PATTERN, v):
            raise ValueError("Phone number must be in E.164 format (e.g., +38164123456)")
        return v


class CustomerResponse(BaseModel):
    id: UUID
    email: str
    phone_number: str | None
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
