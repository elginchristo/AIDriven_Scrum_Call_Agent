# app/config.py - Corrected config with proper imports
import os
import secrets
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database configuration settings"""
    MONGO_URI: str = Field(..., description="MongoDB connection URI")
    DATABASE_NAME: str = Field(..., description="MongoDB database name")


class RedisSettings(BaseModel):
    """Redis configuration settings"""
    HOST: str = Field("localhost", description="Redis host")
    PORT: int = Field(6379, description="Redis port")
    PASSWORD: Optional[str] = Field(None, description="Redis password")
    DB: int = Field(0, description="Redis database index")


class OpenAISettings(BaseModel):
    """OpenAI API configuration settings"""
    API_KEY: str = Field(..., description="OpenAI API key")
    ORGANIZATION: Optional[str] = Field(None, description="OpenAI organization ID")
    MODEL: str = Field("gpt-4", description="OpenAI model to use")


class GoogleCloudSettings(BaseModel):
    """Google Cloud configuration settings"""
    PROJECT_ID: str = Field(..., description="Google Cloud project ID")
    CREDENTIALS_FILE: Optional[str] = Field(None, description="Path to credentials file")
    CREDENTIALS_JSON: Optional[str] = Field(None, description="JSON credentials string")


class ZoomSettings(BaseModel):
    """Zoom API configuration settings"""
    CLIENT_ID: str = Field(..., description="Zoom client ID")
    CLIENT_SECRET: str = Field(..., description="Zoom client secret")
    REDIRECT_URI: str = Field(..., description="Zoom OAuth redirect URI")


class JiraSettings(BaseModel):
    """JIRA API configuration settings"""
    BASE_URL: str = Field(..., description="JIRA base URL")
    API_TOKEN: str = Field(..., description="JIRA API token")
    USERNAME: str = Field(..., description="JIRA username")


class EmailSettings(BaseModel):
    """Email service configuration settings"""
    SMTP_SERVER: str = Field("smtp.gmail.com", description="SMTP server")
    SMTP_PORT: int = Field(587, description="SMTP port")
    USERNAME: str = Field(..., description="Email username")
    PASSWORD: str = Field(..., description="Email password")
    USE_TLS: bool = Field(True, description="Use TLS for SMTP")
    FROM_EMAIL: str = Field(..., description="From email address")


class CelerySettings(BaseModel):
    """Celery configuration settings"""
    BROKER_URL: str = Field(..., description="Celery broker URL")
    RESULT_BACKEND: str = Field(..., description="Celery result backend")
    TASK_SERIALIZER: str = Field("json", description="Task serializer")
    RESULT_SERIALIZER: str = Field("json", description="Result serializer")
    ACCEPT_CONTENT: List[str] = Field(["json"], description="Accepted content types")
    TIMEZONE: str = Field("UTC", description="Timezone")
    ENABLE_UTC: bool = Field(True, description="Enable UTC")


class SecuritySettings(BaseModel):
    """Security configuration settings"""
    SECRET_KEY: str = Field(secrets.token_urlsafe(32), description="Secret key for JWT")
    TOKEN_EXPIRE_MINUTES: int = Field(60 * 24, description="Token expiration time in minutes")
    ALGORITHM: str = Field("HS256", description="JWT algorithm")


class Settings(BaseSettings):
    """Application settings"""
    # Core settings
    APP_NAME: str = Field("AI-Driven Scrum Call Agent", description="Application name")
    ENV: str = Field("development", description="Environment (development, staging, production)")
    DEBUG: bool = Field(False, description="Debug mode")
    API_PREFIX: str = Field("/api", description="API prefix")
    CORS_ORIGINS: List[str] = Field(["*"], description="CORS allowed origins")

    # Component settings
    DATABASE: DatabaseSettings
    REDIS: RedisSettings
    OPENAI: OpenAISettings
    GOOGLE_CLOUD: GoogleCloudSettings
    ZOOM: ZoomSettings
    JIRA: JiraSettings
    EMAIL: EmailSettings
    CELERY: CelerySettings
    SECURITY: SecuritySettings

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field("json", description="Logging format (json or text)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


# Load configuration
settings = Settings()
