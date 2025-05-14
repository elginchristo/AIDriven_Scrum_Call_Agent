# app/schemas/blocker.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.utils.constants import BLOCKER_STATUS_OPEN, BLOCKER_STATUS_RESOLVED

class BlockerBase(BaseModel):
    """Base blocker schema."""
    project_id: str
    blocked_item_id: str
    blocked_item_title: str
    assignee: str
    blocker_description: str
    blocking_reason: str
    status: str = BLOCKER_STATUS_OPEN

class BlockerCreate(BlockerBase):
    """Blocker creation schema."""
    pass

class BlockerUpdate(BaseModel):
    """Blocker update schema."""
    blocker_description: Optional[str] = None
    blocking_reason: Optional[str] = None
    resolved_date: Optional[datetime] = None
    status: Optional[str] = None

class BlockerInDB(BlockerBase):
    """Blocker in database schema."""
    id: str
    blocker_raised_date: datetime
    resolved_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class BlockerResponse(BlockerBase):
    """Blocker response schema."""
    id: Optional[str] = None
    blocker_raised_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
