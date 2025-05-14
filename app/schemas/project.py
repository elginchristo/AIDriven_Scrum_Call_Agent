# app/schemas/project.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ProjectBase(BaseModel):
    """Base project schema."""
    project_id: str = Field(..., min_length=3, max_length=50)
    project_key: str = Field(..., min_length=2, max_length=10)
    project_name: str = Field(..., min_length=3, max_length=100)
    project_type: str
    project_lead: str
    project_description: Optional[str] = None
    project_url: Optional[str] = None
    project_category: Optional[str] = None

class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass

class ProjectUpdate(BaseModel):
    """Project update schema."""
    project_name: Optional[str] = Field(None, min_length=3, max_length=100)
    project_type: Optional[str] = None
    project_lead: Optional[str] = None
    project_description: Optional[str] = None
    project_url: Optional[str] = None
    project_category: Optional[str] = None

class ProjectInDB(ProjectBase):
    """Project in database schema."""
    id: str
    created_at: datetime
    updated_at: datetime

class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
