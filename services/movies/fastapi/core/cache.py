from abc import ABC, abstractmethod
from functools import lru_cache

import orjson
from fastapi import Depends, Request
from redis.asyncio import Redis
from pydantic import BaseModel

from core.config import settings
from db.redis import get_redis_instance


class AbstractCacheService(ABC):
    """Абстрактный класс-интерфейс для сервисов кэширования"""

    @abstractmethod
    async def get_instances_from_cache(
        self, request: Request, model: BaseModel
    ) -> list[BaseModel | None]:
        """Абстрактый метод получения списка объектов, хранящихся в кэше"""

    @abstractmethod
    async def put_instances_to_cache(
        self, request: Request, instances: list[BaseModel]
    ) -> None:
        """Абстрактный метод сохранения списка объектов в кэш"""


class ExtractKeyFromRequest:
    @staticmethod
    def _calc_key(request: Request) -> str:
        """Общий метод получения параметра key для сервисов кэширования"""
        return str(request.url)


class RedisService(AbstractCacheService, ExtractKeyFromRequest):
    def __init__(self, redis_instance: Redis) -> None:
        self.redis = redis_instance

    async def get_instances_from_cache(
        self, request: Request, model: BaseModel
    ) -> list[BaseModel | None]:
        """Метод получения списка объектов, хранящихся в кэше Redis"""
        key = self._calc_key(request)
        instances = []
        json_data = await self.redis.get(key)
        if json_data:
            for data in orjson.loads(json_data):
                instances.append(model.parse_raw(data))
        return instances

    async def put_instances_to_cache(
        self, request: Request, instances: list[BaseModel]
    ) -> None:
        """Метод сохранения списка объектов в кэш Redis"""
        key = self._calc_key(request)
        json = orjson.dumps(
            [instance.json() for instance in instances]
        ).decode()
        await self.redis.set(
            name=key, value=json, ex=settings.CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_cache_service(
    redis_instance: Redis = Depends(get_redis_instance),
) -> AbstractCacheService:
    return RedisService(redis_instance)
