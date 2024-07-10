from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import BaseModel

from core.exceptions import ElasticsearchError
from core.logger import logger
from db.elastic import get_elastic_instance


class AbstractStorage(ABC):
    """Абстрактный класс-интерфейс для реализации хранилищ данных"""

    @abstractmethod
    async def get_one_by_id(
        self, index: str, model_class: BaseModel, uuid: UUID
    ) -> BaseModel | None:
        """Абстрактный метод получения инстанса указанной модели
        по id документа в хранилище
        """

    @abstractmethod
    async def get_list_by_search(
        self, index: str, model_class: BaseModel, query: str
    ) -> list[BaseModel] | None:
        """Абстрактный метод получения списка инстансов указанной модели
        по заданным параметрам поиска
        """


class ElasticService(AbstractStorage):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get_one_by_id(
        self, index: str, model_class: Any, uuid: UUID
    ) -> BaseModel | None:
        try:
            doc = await self.elastic.get(index=index, id=str(uuid))
            return model_class(**doc["_source"])
        except NotFoundError:
            return None

    async def get_list_by_search(
        self, index: str, model_class: Any, query: str
    ) -> list[BaseModel] | None:
        try:
            search_result = await self.elastic.search(index=index, body=query)
            list_instances = [
                model_class(**doc["_source"])
                for doc in search_result["hits"]["hits"]
            ]
            return list_instances
        except ElasticsearchError as e:
            logger.error(f"Ошибка Elasticsearch: {e}")
            return None


@lru_cache()
def get_storage_service(
    elastic_instance: AsyncElasticsearch = Depends(get_elastic_instance),
) -> AbstractStorage:
    return ElasticService(elastic_instance)
