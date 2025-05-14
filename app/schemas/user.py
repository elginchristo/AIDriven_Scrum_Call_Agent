# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """User in database schema."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserResponse(UserBase):
    """User response schema."""
    id: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: str  # User ID
    exp: int  # Expiration time (Unix timestamp)
