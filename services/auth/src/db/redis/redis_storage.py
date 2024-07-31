from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis

from db.redis.cache_storage import BaseCacheStorage
from db.redis.redis import get_redis


class RedisStorage(BaseCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def put_to_cache(self, key, value, lifetime=None):
        """Put a key-value data into cache."""
        await self.redis.set(name=key, value=value, ex=lifetime)

    async def get_from_cache(self, key):
        """Get a key-value data from cache."""
        data = await self.redis.get(name=key)
        return data


@lru_cache(maxsize=1)
def get_redis_storage(
    redis: Redis = Depends(get_redis),
) -> RedisStorage:
    return RedisStorage(redis)
