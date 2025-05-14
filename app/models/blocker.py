# app/models/blocker.py
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class BlockerStatus(str, Enum):
    """Blocker status enum."""
    OPEN = "Open"
    RESOLVED = "Resolved"

class BlockerModel(MongoBaseModel):
    """Blocker model."""
    project_id: str = Field(..., description="Project ID")
    blocked_item_id: str = Field(..., description="Blocked item ID")
    blocked_item_title: str = Field(..., description="Blocked item title")
    assignee: str = Field(..., description="Assignee")
    blocker_description: str = Field(..., description="Blocker description")
    blocker_raised_date: datetime = Field(default_factory=datetime.utcnow, description="Blocker raised date")
    blocking_reason: str = Field(..., description="Blocking reason")
    resolved_date: Optional[datetime] = Field(None, description="Resolved date")
    status: BlockerStatus = Field(BlockerStatus.OPEN, description="Status")
