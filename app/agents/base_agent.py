# app/agents/base_agent.py - Corrected base agent
import logging
import json
import asyncio
from abc import ABC, abstractmethod
from redis import Redis
from app.config import settings
import openai

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, call_id, redis_client):
        """Initialize the base agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
        """
        self.call_id = call_id
        self.redis = redis_client

        # Set up OpenAI client
        openai.api_key = settings.OPENAI.API_KEY
        if settings.OPENAI.ORGANIZATION:
            openai.organization = settings.OPENAI.ORGANIZATION

    async def store_data(self, key, data, expiry=3600):
        """Store data in Redis."""
        try:
            redis_key = f"call:{self.call_id}:{key}"
            self.redis.set(redis_key, json.dumps(data), ex=expiry)
            logger.debug(f"Stored data with key: {redis_key}")
        except Exception as e:
            logger.error(f"Failed to store data in Redis: {str(e)}")

    async def retrieve_data(self, key):
        """Retrieve data from Redis."""
        try:
            redis_key = f"call:{self.call_id}:{key}"
            data = self.redis.get(redis_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve data from Redis: {str(e)}")
            return None

    async def delete_data(self, key):
        """Delete data from Redis."""
        try:
            redis_key = f"call:{self.call_id}:{key}"
            self.redis.delete(redis_key)
            logger.debug(f"Deleted data with key: {redis_key}")
        except Exception as e:
            logger.error(f"Failed to delete data from Redis: {str(e)}")

    async def call_openai(self, messages, model=None, temperature=0.2, max_tokens=2000):
        """Call the OpenAI API."""
        try:
            model = model or settings.OPENAI.MODEL

            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    @abstractmethod
    async def process(self, *args, **kwargs):
        """Process data. To be implemented by subclasses."""
        pass

