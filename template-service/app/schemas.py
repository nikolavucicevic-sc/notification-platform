from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.template import ChannelType


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    channel_type: ChannelType = Field(default=ChannelType.EMAIL, description="Channel type (EMAIL or SMS)")
    subject: Optional[str] = Field(None, max_length=500, description="Email subject (required for EMAIL)")
    body: str = Field(..., min_length=1, description="Template body")
    variables: Optional[List[str]] = Field(default=[], description="List of variables used in template")


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    channel_type: Optional[ChannelType] = None
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateRenderRequest(BaseModel):
    template_id: str = Field(..., description="Template ID to render")
    variables: dict = Field(..., description="Variables to substitute in template")


class TemplateRenderResponse(BaseModel):
    subject: Optional[str] = None
    body: str
    channel_type: ChannelType
    variables_used: List[str]
    missing_variables: List[str] = []
