# app/schemas/sprint.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class BurndownPoint(BaseModel):
    """Burndown point schema."""
    date: datetime
    remaining_points: float

class SprintBase(BaseModel):
    """Base sprint schema."""
    project_id: str
    sprint_id: str
    sprint_name: str
    start_date: datetime
    end_date: datetime
    total_story_points: float = 0
    completed_story_points: float = 0
    percent_completion: float = 0
    remaining_story_points: float = 0

class SprintCreate(SprintBase):
    """Sprint creation schema."""
    pass

class SprintUpdate(BaseModel):
    """Sprint update schema."""
    sprint_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_story_points: Optional[float] = None
    completed_story_points: Optional[float] = None
    remaining_story_points: Optional[float] = None

class SprintInDB(SprintBase):
    """Sprint in database schema."""
    id: str
    burndown_trend: List[BurndownPoint]
    created_at: datetime
    updated_at: datetime

class SprintResponse(SprintBase):
    """Sprint response schema."""
    id: Optional[str] = None
    burndown_trend: Optional[List[BurndownPoint]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
