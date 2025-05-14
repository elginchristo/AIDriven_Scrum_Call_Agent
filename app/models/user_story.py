# app/models/user_story.py
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class StoryStatus(str, Enum):
    """User story status enum."""
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class StoryPriority(str, Enum):
    """User story priority enum."""
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"

class WorkItemType(str, Enum):
    """Work item type enum."""
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"
    SPIKE = "Spike"

class UserStoryModel(MongoBaseModel):
    """User story model."""
    project_id: str = Field(..., description="Project ID")
    sprint_id: str = Field(..., description="Sprint ID")
    story_id: str = Field(..., description="Story ID")
    story_title: str = Field(..., description="Story title")
    assignee: str = Field(..., description="Assignee")
    status: StoryStatus = Field(StoryStatus.TODO, description="Status")
    priority: StoryPriority = Field(StoryPriority.MEDIUM, description="Priority")
    story_points: float = Field(0, description="Story points")
    work_item_type: WorkItemType = Field(WorkItemType.TASK, description="Work item type")
    days_in_current_status: int = Field(0, description="Days in current status")
    last_status_change_date: datetime = Field(default_factory=datetime.utcnow, description="Last status change date")
