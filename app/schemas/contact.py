# app/schemas/contact.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ContactDetailsBase(BaseModel):
    """Base contact details schema."""
    team_name: str
    name: str
    email: EmailStr

class ContactDetailsCreate(ContactDetailsBase):
    """Contact details creation schema."""
    pass

class ContactDetailsUpdate(BaseModel):
    """Contact details update schema."""
    team_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class ContactDetailsResponse(ContactDetailsBase):
    """Contact details response schema."""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
