from redis.asyncio import Redis

redis: Redis | None = None


async def get_redis_instance() -> Redis:
    return redis
