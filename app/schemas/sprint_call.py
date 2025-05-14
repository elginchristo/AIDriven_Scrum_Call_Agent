# app/schemas/sprint_call.py
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class BlockerItem(BaseModel):
    """Blocker item schema for sprint call."""
    item_id: str
    description: str
    assignee: str

class DelayItem(BaseModel):
    """Delay item schema for sprint call."""
    item_id: str
    reason: str
    estimated_recovery: str

class SprintCallBase(BaseModel):
    """Base sprint call schema."""
    project_name: str
    team_name: str
    date_time: datetime
    scrum_summary: str
    participants: List[str] = []
    missing_participants: List[str] = []
    blockers: List[BlockerItem] = []
    delays: List[DelayItem] = []
    transcript_url: Optional[str] = None
    recording_url: Optional[str] = None

class SprintCallInDB(SprintCallBase):
    """Sprint call in database schema."""
    id: str
    created_at: datetime
    updated_at: datetime

class SprintCallResponse(SprintCallBase):
    """Sprint call response schema."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
