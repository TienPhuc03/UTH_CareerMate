import json
from typing import Any, Optional

import redis

from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client wrapper."""

    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
            )
            self.client.ping()
            self.is_connected = True
            logger.info(f"Redis connected: {settings.REDIS_URL}")
        except Exception as exc:
            self.is_connected = False
            logger.warning(f"Redis not available: {exc}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.is_connected:
            return None
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as exc:
            logger.error(f"Redis GET error: {exc}")
            return None

    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Set value in cache."""
        if not self.is_connected:
            return False
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if expire is None:
                expire = settings.REDIS_CACHE_EXPIRATION
            self.client.setex(key, expire, serialized)
            logger.debug(f"Cache SET: {key} (expires in {expire}s)")
            return True
        except Exception as exc:
            logger.error(f"Redis SET error: {exc}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.is_connected:
            return False
        try:
            result = self.client.delete(key)
            if result:
                logger.debug(f"Cache DELETE: {key}")
            return bool(result)
        except Exception as exc:
            logger.error(f"Redis DELETE error: {exc}")
            return False

    def get_int(self, key: str) -> Optional[int]:
        """Get an integer value from Redis without JSON decoding."""
        if not self.is_connected:
            return None
        try:
            value = self.client.get(key)
            if value is None:
                return 0
            return int(value)
        except Exception as exc:
            logger.error(f"Redis GET INT error: {exc}")
            return None

    def ttl(self, key: str) -> Optional[int]:
        """Get TTL for a Redis key in seconds."""
        if not self.is_connected:
            return None
        try:
            ttl = self.client.ttl(key)
            if ttl is None or ttl < 0:
                return 0
            return int(ttl)
        except Exception as exc:
            logger.error(f"Redis TTL error: {exc}")
            return None

    def increment_counter(self, key: str, expire: int) -> Optional[tuple[int, int]]:
        """Atomically increment a counter and ensure it has an expiration."""
        if not self.is_connected:
            return None
        try:
            pipeline = self.client.pipeline()
            pipeline.incr(key)
            pipeline.ttl(key)
            count, ttl = pipeline.execute()

            if count == 1 or ttl is None or ttl < 0:
                self.client.expire(key, expire)
                ttl = expire

            return int(count), int(ttl)
        except Exception as exc:
            logger.error(f"Redis INCR error: {exc}")
            return None

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not self.is_connected:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.debug(f"Deleted {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as exc:
            logger.error(f"Redis DELETE PATTERN error: {exc}")
            return 0

    def get_info(self) -> dict:
        """Get Redis info."""
        if not self.is_connected:
            return {"status": "disconnected"}
        try:
            info = self.client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "total_keys": self.client.dbsize(),
            }
        except Exception as exc:
            return {"status": "error", "error": str(exc)}


redis_client = RedisClient()


def get_cv_cache_key(cv_id: int) -> str:
    return f"cv:analysis:{cv_id}"


def get_job_recommendations_key(cv_id: int) -> str:
    return f"job:recommendations:{cv_id}"
