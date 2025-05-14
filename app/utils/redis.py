# app/utils/redis.py - Corrected Redis utility
import logging
import json
from redis import Redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Client for interacting with Redis."""

    def __init__(self):
        """Initialize the Redis client."""
        self.redis = Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            password=settings.REDIS.PASSWORD,
            db=settings.REDIS.DB,
            decode_responses=True  # Automatically decode responses to strings
        )

    def ping(self):
        """Test connection to Redis."""
        try:
            return self.redis.ping()
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            return False

    def set(self, key, value, ex=None):
        """Set a key-value pair in Redis."""
        try:
            # JSON serialize if value is not a string
            if not isinstance(value, str):
                value = json.dumps(value)

            return self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    def get(self, key):
        """Get a value from Redis."""
        try:
            value = self.redis.get(key)

            # Try to JSON parse the value
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value

            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    def delete(self, key):
        """Delete a key from Redis."""
        try:
            return self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return 0

    def keys(self, pattern):
        """Get keys matching a pattern."""
        try:
            return self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error: {str(e)}")
            return []

    def publish(self, channel, message):
        """Publish a message to a channel."""
        try:
            # JSON serialize if message is not a string
            if not isinstance(message, str):
                message = json.dumps(message)

            return self.redis.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish error: {str(e)}")
            return 0


# Initialize Redis client
redis_client = RedisClient()
