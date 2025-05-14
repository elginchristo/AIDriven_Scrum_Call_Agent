# app/schemas/scheduled_call.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.constants import (
    PLATFORM_ZOOM, DEFAULT_AGGRESSIVENESS, DEFAULT_CRON_PATTERN
)

class PlatformCredentials(BaseModel):
    """Platform credentials schema."""
    username: str
    password: str

class EmailCredentials(BaseModel):
    """Email credentials schema."""
    username: str
    password: str

class ScheduledCallBase(BaseModel):
    """Base scheduled call schema."""
    team_name: str
    project_name: str
    scheduled_time: datetime
    platform: str = PLATFORM_ZOOM
    platform_credentials: PlatformCredentials
    email_credentials: EmailCredentials
    aggressiveness_level: int = Field(DEFAULT_AGGRESSIVENESS, ge=1, le=10)
    is_recurring: bool = True
    recurring_pattern: str = DEFAULT_CRON_PATTERN

class ScheduledCallCreate(ScheduledCallBase):
    """Scheduled call creation schema."""
    pass

class ScheduledCallUpdate(BaseModel):
    """Scheduled call update schema."""
    team_name: Optional[str] = None
    project_name: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    platform: Optional[str] = None
    platform_credentials: Optional[PlatformCredentials] = None
    email_credentials: Optional[EmailCredentials] = None
    aggressiveness_level: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_pattern: Optional[str] = None

class ScheduledCallInDB(ScheduledCallBase):
    """Scheduled call in database schema."""
    id: str
    status: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ScheduledCallResponse(ScheduledCallBase):
    """Scheduled call response schema."""
    id: Optional[str] = None
    status: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
