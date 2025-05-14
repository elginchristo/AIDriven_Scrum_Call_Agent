# app/models/sprint_call.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field  # Added BaseModel import
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class BlockerItem(BaseModel):
    """Blocker item model for sprint call."""
    item_id: str = Field(..., description="Item ID")
    description: str = Field(..., description="Description")
    assignee: str = Field(..., description="Assignee")

class DelayItem(BaseModel):
    """Delay item model for sprint call."""
    item_id: str = Field(..., description="Item ID")
    reason: str = Field(..., description="Reason")
    estimated_recovery: str = Field(..., description="Estimated recovery")

class SprintCallModel(MongoBaseModel):
    """Sprint call model."""
    project_name: str = Field(..., description="Project name")
    team_name: str = Field(..., description="Team name")
    date_time: datetime = Field(..., description="Date and time")
    scrum_summary: str = Field(..., description="Scrum summary")
    participants: List[str] = Field(default_factory=list, description="Participants")
    missing_participants: List[str] = Field(default_factory=list, description="Missing participants")
    blockers: List[BlockerItem] = Field(default_factory=list, description="Blockers")
    delays: List[DelayItem] = Field(default_factory=list, description="Delays")
    transcript_url: Optional[str] = Field(None, description="Transcript URL")
    recording_url: Optional[str] = Field(None, description="Recording URL")
