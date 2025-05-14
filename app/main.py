# app/main.py - Fixed version with proper initialization order
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.router import api_router
from app.services.database import connect_to_mongo, close_mongo_connection, get_database
from app.services.scheduler import initialize_scheduler
from app.utils.logger import setup_logging
from app.config import settings


# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize database connection first
        logger.info("Connecting to MongoDB...")
        await connect_to_mongo()
        logger.info("Connected to MongoDB successfully")

        # Initialize scheduler after database is connected
        logger.info("Initializing scheduler...")
        scheduler = initialize_scheduler()
        scheduler.start()
        logger.info("Scheduler started successfully")

        # Yield control back to FastAPI
        yield

        # Shutdown operations
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()

        logger.info("Closing MongoDB connection...")
        await close_mongo_connection()

    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise


# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Scrum Call Agent",
    description="Automated Scrum Call Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


# Default root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Driven Scrum Call Agent API"}


# Health check endpoint
@app.get("/health")
async def health_check():
    # Check database connection
    try:
        db = get_database()
        # Perform a simple operation to test connection
        await db.list_collection_names()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "environment": settings.ENV,
        "database": db_status
    }