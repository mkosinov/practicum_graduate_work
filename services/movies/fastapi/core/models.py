"""Конфигурационные модели."""
from enum import Enum
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonDumps(BaseModel):
    """Абстрактная модель. Меняет стандартный медленный json на orjson."""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

    class Meta:
        abstract = True


class Base(OrjsonDumps):
    """Абстрактная модель. Добавляет ID."""

    uuid: UUID

    class Meta:
        abstract = True


class SortOrder(str, Enum):
    """Модель сортировки результатов API."""

    ascending = "asc"
    descending = "desc"
