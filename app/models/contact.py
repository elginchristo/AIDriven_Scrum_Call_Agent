# app/models/contact.py
from app.models.base import MongoBaseModel, PyObjectId
from pydantic import Field, EmailStr

class ContactDetailsModel(MongoBaseModel):
    """Contact details model."""
    team_name: str = Field(..., description="Team name")
    name: str = Field(..., description="Name")
    email: EmailStr = Field(..., description="Email address")
