# app/models/velocity.py
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class VelocityHistoryModel(MongoBaseModel):
    """Velocity history model."""
    project_id: str = Field(..., description="Project ID")
    sprint_id: str = Field(..., description="Sprint ID")
    story_points_committed: float = Field(..., description="Story points committed")
    story_points_completed: float = Field(..., description="Story points completed")
    velocity: float = Field(..., description="Velocity")
    deviation: float = Field(..., description="Deviation percentage")