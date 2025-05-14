# app/models/scheduled_call.py
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import BaseModel, Field  # Added BaseModel import
from pydantic import Field

class PlatformType(str, Enum):
    """Meeting platform type enum."""
    ZOOM = "zoom"
    TEAMS = "teams"
    MEET = "meet"

class CallStatus(str, Enum):
    """Call status enum."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PlatformCredentials(BaseModel):
    """Platform credentials model."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class EmailCredentials(BaseModel):
    """Email credentials model."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class ScheduledCallModel(MongoBaseModel):
    """Scheduled call model."""
    team_name: str = Field(..., description="Team name")
    project_name: str = Field(..., description="Project name")
    scheduled_time: datetime = Field(..., description="Scheduled time")
    platform: PlatformType = Field(PlatformType.ZOOM, description="Platform")
    platform_credentials: PlatformCredentials = Field(..., description="Platform credentials")
    email_credentials: EmailCredentials = Field(..., description="Email credentials")
    aggressiveness_level: int = Field(5, ge=1, le=10, description="Aggressiveness level")
    status: CallStatus = Field(CallStatus.SCHEDULED, description="Status")
    last_run: Optional[datetime] = Field(None, description="Last run")
    next_run: Optional[datetime] = Field(None, description="Next run")
    is_recurring: bool = Field(True, description="Is recurring")
    recurring_pattern: str = Field("0 10 * * 1-5", description="Recurring pattern") # Cron expression: weekdays at 10 AM
