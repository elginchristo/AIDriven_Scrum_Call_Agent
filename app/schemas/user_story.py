# app/schemas/user_story.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.constants import (
    STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_BLOCKED,
    PRIORITY_HIGHEST, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_LOWEST,
    WORK_ITEM_STORY, WORK_ITEM_TASK, WORK_ITEM_BUG, WORK_ITEM_SPIKE
)

class UserStoryBase(BaseModel):
    """Base user story schema."""
    project_id: str
    sprint_id: str
    story_id: str
    story_title: str
    assignee: str
    status: str = STATUS_TODO
    priority: str = PRIORITY_MEDIUM
    story_points: float = 0
    work_item_type: str = WORK_ITEM_TASK

class UserStoryCreate(UserStoryBase):
    """User story creation schema."""
    pass

class UserStoryUpdate(BaseModel):
    """User story update schema."""
    story_title: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    story_points: Optional[float] = None
    work_item_type: Optional[str] = None

class UserStoryInDB(UserStoryBase):
    """User story in database schema."""
    id: str
    days_in_current_status: int
    last_status_change_date: datetime
    created_at: datetime
    updated_at: datetime

class UserStoryResponse(UserStoryBase):
    """User story response schema."""
    id: Optional[str] = None
    days_in_current_status: Optional[int] = None
    last_status_change_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
