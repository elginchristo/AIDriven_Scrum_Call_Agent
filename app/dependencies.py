# app/dependencies.py - Version without any authentication
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.config import settings

# Simple database dependency
async def get_db():
    """Get database instance."""
    return get_database()

# Settings dependency
def get_settings():
    """Get application settings."""
    return settings

# Pagination parameters
def get_pagination_params(skip: int = 0, limit: int = 100):
    """Common pagination parameters."""
    return {
        "skip": max(0, skip),
        "limit": min(1000, limit)
    }
