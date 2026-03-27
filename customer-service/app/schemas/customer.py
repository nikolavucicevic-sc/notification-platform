from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID
import re
import bleach


class CustomerCreate(BaseModel):
    email: EmailStr  # Validates email format
    phone_number: str | None = Field(
        None,
        regex=r"^\+[1-9]\d{1,14}$",  # E.164 format: +1234567890
        description="Phone number in E.164 format (e.g., +1234567890)"
    )
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        """Remove HTML tags and dangerous characters from names."""
        if v:
            # Remove HTML tags
            cleaned = bleach.clean(v, tags=[], strip=True)
            # Remove excessive whitespace
            cleaned = " ".join(cleaned.split())
            return cleaned
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        """Additional phone validation."""
        if v and not re.match(r"^\+[1-9]\d{1,14}$", v):
            raise ValueError(
                "Phone number must be in E.164 format (e.g., +1234567890)"
            )
        return v


class CustomerUpdate(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = Field(
        None,
        regex=r"^\+[1-9]\d{1,14}$",
        description="Phone number in E.164 format"
    )
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)

    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        """Remove HTML tags and dangerous characters from names."""
        if v:
            cleaned = bleach.clean(v, tags=[], strip=True)
            cleaned = " ".join(cleaned.split())
            return cleaned
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        """Additional phone validation."""
        if v and not re.match(r"^\+[1-9]\d{1,14}$", v):
            raise ValueError(
                "Phone number must be in E.164 format (e.g., +1234567890)"
            )
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