# app/schemas/team_capacity.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TeamCapacityBase(BaseModel):
    """Base team capacity schema."""
    project_id: str
    sprint_id: str
    team_member: str
    available_hours: float = Field(..., ge=0, description="Available hours in sprint")
    allocated_hours: float = Field(..., ge=0, description="Allocated hours")
    remaining_hours: float = Field(..., ge=0, description="Remaining hours")
    days_off: int = Field(0, ge=0, description="Days off during sprint")

class TeamCapacityCreate(TeamCapacityBase):
    """Team capacity creation schema."""
    pass

class TeamCapacityUpdate(BaseModel):
    """Team capacity update schema."""
    available_hours: Optional[float] = Field(None, ge=0)
    allocated_hours: Optional[float] = Field(None, ge=0)
    remaining_hours: Optional[float] = Field(None, ge=0)
    days_off: Optional[int] = Field(None, ge=0)

class TeamCapacityResponse(TeamCapacityBase):
    """Team capacity response schema."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
