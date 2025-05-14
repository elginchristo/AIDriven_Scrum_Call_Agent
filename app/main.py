# app/main.py - Main application without authentication
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.router import api_router
from app.services.database import connect_to_mongo, close_mongo_connection, get_database
from app.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan event handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Scrum Agent API (No Authentication)")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")

    yield

    # Shutdown
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")


# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Scrum Call Agent",
    description="Open API - No authentication required",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Scrum Agent API",
        "authentication": "disabled",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        db = get_database()
        await db.list_collection_names()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "authentication": "disabled"
    }