from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class CustomerCreate(BaseModel):
    email: str
    phone_number: str | None = None
    first_name: str
    last_name: str


class CustomerUpdate(BaseModel):
    email: str | None = None
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None


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