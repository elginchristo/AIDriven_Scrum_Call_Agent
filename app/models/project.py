# app/models/project.py
from typing import Optional
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field

class ProjectModel(MongoBaseModel):
    """Project model."""
    project_id: str = Field(..., description="Project ID")
    project_key: str = Field(..., description="Project key")
    project_name: str = Field(..., description="Project name")
    project_type: str = Field(..., description="Project type")
    project_lead: str = Field(..., description="Project lead")
    project_description: Optional[str] = Field(None, description="Project description")
    project_url: Optional[str] = Field(None, description="Project URL")
    project_category: Optional[str] = Field(None, description="Project category")
