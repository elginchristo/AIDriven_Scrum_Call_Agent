# app/schemas/velocity.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class VelocityHistoryBase(BaseModel):
    """Base velocity history schema."""
    project_id: str
    sprint_id: str
    story_points_committed: float = Field(..., ge=0, description="Story points committed")
    story_points_completed: float = Field(..., ge=0, description="Story points completed")
    velocity: float = Field(..., ge=0, description="Sprint velocity")
    deviation: float = Field(..., description="Deviation percentage")

class VelocityHistoryCreate(VelocityHistoryBase):
    """Velocity history creation schema."""
    pass

class VelocityHistoryUpdate(BaseModel):
    """Velocity history update schema."""
    story_points_committed: Optional[float] = Field(None, ge=0)
    story_points_completed: Optional[float] = Field(None, ge=0)
    velocity: Optional[float] = Field(None, ge=0)
    deviation: Optional[float] = None

class VelocityHistoryResponse(VelocityHistoryBase):
    """Velocity history response schema."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None