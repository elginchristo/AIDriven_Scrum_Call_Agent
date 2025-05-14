# app/models/team_capacity.py
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class TeamCapacityModel(MongoBaseModel):
    """Team capacity model."""
    project_id: str = Field(..., description="Project ID")
    sprint_id: str = Field(..., description="Sprint ID")
    team_member: str = Field(..., description="Team member")
    available_hours: float = Field(..., description="Available hours")
    allocated_hours: float = Field(..., description="Allocated hours")
    remaining_hours: float = Field(..., description="Remaining hours")
    days_off: int = Field(0, description="Days off")
