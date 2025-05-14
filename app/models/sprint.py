# app/models/sprint.py
from typing import Optional, List, Dict
from datetime import datetime
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field
from pydantic import BaseModel, Field  # Added BaseModel import

class BurndownPoint(BaseModel):
    """Burndown point model."""
    date: datetime = Field(..., description="Burndown date")
    remaining_points: float = Field(..., description="Remaining points")

class SprintProgressModel(MongoBaseModel):
    """Sprint progress model."""
    project_id: str = Field(..., description="Project ID")
    sprint_id: str = Field(..., description="Sprint ID")
    sprint_name: str = Field(..., description="Sprint name")
    start_date: datetime = Field(..., description="Sprint start date")
    end_date: datetime = Field(..., description="Sprint end date")
    total_story_points: float = Field(0, description="Total story points")
    completed_story_points: float = Field(0, description="Completed story points")
    percent_completion: float = Field(0, description="Percentage completion")
    remaining_story_points: float = Field(0, description="Remaining story points")
    burndown_trend: List[BurndownPoint] = Field(default_factory=list, description="Burndown trend")
