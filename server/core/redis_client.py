
import redis
import json
from typing import Any, Optional
from core.config import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()
            self.is_connected = True
            logger.info(f"✅ Redis connected: {settings.REDIS_URL}")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"⚠️  Redis not available: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.is_connected:
            return None
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Set value in cache"""
        if not self.is_connected:
            return False
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if expire is None:
                expire = settings.REDIS_CACHE_EXPIRATION
            self.client.setex(key, expire, serialized)
            logger.debug(f"Cache SET: {key} (expires in {expire}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.is_connected:
            return False
        try:
            result = self.client.delete(key)
            if result:
                logger.debug(f"Cache DELETE: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        if not self.is_connected:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.debug(f"Deleted {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE PATTERN error: {e}")
            return 0
    
    def get_info(self) -> dict:
        """Get Redis info"""
        if not self.is_connected:
            return {"status": "disconnected"}
        try:
            info = self.client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "total_keys": self.client.dbsize()
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global instance
redis_client = RedisClient()


# Helper functions
def get_cv_cache_key(cv_id: int) -> str:
    return f"cv:analysis:{cv_id}"


def get_job_recommendations_key(cv_id: int) -> str:
    return f"job:recommendations:{cv_id}"