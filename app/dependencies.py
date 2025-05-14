# app/dependencies.py - Development-friendly version
from typing import Optional
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.config import settings

# Simple database dependency
async def get_db() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return get_database()

# Development user dependency - returns a dummy user without authentication
async def get_current_user(db: AsyncIOMotorDatabase = Depends(get_db)) -> dict:
    """
    Get current user - returns dummy user in development mode.
    """
    if settings.ENV == "development":
        # Return a dummy user for development
        return {
            "_id": "dev_user_123",
            "username": "dev_user",
            "email": "dev@example.com",
            "is_admin": True,
            "is_active": True
        }
    else:
        # In production, implement proper authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional user dependency
async def get_current_user_optional(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Optional[dict]:
    """Optional user dependency."""
    try:
        return await get_current_user(db)
    except:
        return None

# Admin user dependency
async def get_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure the current user is an admin.
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Pagination parameters
def get_pagination_params(skip: int = 0, limit: int = 100) -> dict:
    """Common pagination parameters."""
    return {
        "skip": max(0, skip),
        "limit": min(1000, limit)
    }

# Settings dependency
def get_settings():
    """Get application settings."""
    return settings