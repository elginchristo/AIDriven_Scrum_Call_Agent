# app/services/database.py
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Connect to MongoDB."""
    logger.info("Connecting to MongoDB...")
    Database.client = AsyncIOMotorClient(settings.DATABASE.MONGO_URI)
    try:
        # Verify connection is successful
        await Database.client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    logger.info("Closing MongoDB connection...")
    if Database.client:
        Database.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance."""
    return Database.client[settings.DATABASE.DATABASE_NAME]
