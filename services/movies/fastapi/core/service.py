"""Общие сервисы для эндроинтов API."""
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel

from core.cache import AbstractCacheService
from core.config import settings
from core.es_queries import (
    BOOL,
    MATCH_ALL,
    MATCH_QUERY,
    NESTED_QUERY,
    QUERY_BASE,
    SORT,
)
from core.models import SortOrder
from core.storage import ElasticService


class CommonService:
    def __init__(
        self,
        cache: AbstractCacheService,
        elastic: ElasticService,
        model: BaseModel,
        index: str,
    ):
        self.cache = cache
        self.elastic = elastic
        self.model = model
        self.index = index

    async def get_by_uuid(
        self, uuid: UUID, request: Request
    ) -> BaseModel | None:
        """Метод поиска в индексе по UUID."""
        if instances := await self.cache.get_instances_from_cache(
            request=request, model=self.model
        ):
            return instances[-1]
        if instance := await self.elastic.get_one_by_id(
            index=self.index, model_class=self.model, uuid=uuid
        ):
            await self.cache.put_instances_to_cache(
                request=request, instances=[instance]
            )
            return instance

    async def get_list(
        self,
        request: Request,
        page_number: int = 1,
        page_size: int = settings.STANDART_PAGE_SIZE,
        sort: str = None,
        matches: dict = None,
        nested_matches: dict = None,
        bool_operator: str = "should",
    ) -> list[BaseModel | None]:
        """Метод получения списка из индекса по заданным параметрам."""
        if instances := await self.cache.get_instances_from_cache(
            request=request, model=self.model
        ):
            return instances
        if sort:
            sort = self._get_sort(sort=sort)
        es_query = self._get_es_query(
            page_number=page_number,
            page_size=page_size,
            sort=sort,
            matches=matches,
            nested_matches=nested_matches,
            bool_operator=bool_operator,
        )
        list_instances = await self.elastic.get_list_by_search(
            index=self.index, model_class=self.model, query=es_query
        )
        if list_instances:
            await self.cache.put_instances_to_cache(
                request=request, instances=list_instances
            )
        return list_instances

    @staticmethod
    def _get_es_query(
        sort: str,
        page_number: int = 1,
        page_size: int = settings.STANDART_PAGE_SIZE,
        matches: dict = None,
        nested_matches: dict = None,
        bool_operator: str = "should",
    ):
        """Метод получения тела запроса в Elasticsearch."""
        if sort is None:
            sort = ""
        bool_base = ""
        bool_nested = ""
        from_ = (page_number - 1) * page_size
        if matches:
            bool_base = ",".join(
                (MATCH_QUERY % {"key": key, "value": value})
                for key, value in matches.items()
            )
        if nested_matches:
            bool_nested = ",".join(
                (
                    NESTED_QUERY
                    % {
                        "key_path": key.split(".")[0],
                        "key": key,
                        "value": value,
                    }
                )  # noqa: F811
                for key, value in nested_matches.items()
            )
        if not bool_base and not bool_nested:
            bool = MATCH_ALL
        else:
            bool = ",".join((bool_base, bool_nested)).strip(",")
            bool = BOOL % {"bool_operator": bool_operator, "bool": bool}
        es_query = QUERY_BASE % {
            "from_": from_,
            "page_size": page_size,
            "sort": sort,
            "bool": bool,
        }
        return es_query

    @staticmethod
    def _get_sort(sort: str):
        """Метод получения параметра sort для запроса в Elasticsearch."""
        direction = SortOrder.ascending
        if sort.startswith("-"):
            sort = sort[1:]
            direction = SortOrder.descending
        sorts = {sort: direction}
        for key, value in sorts.items():
            sort = SORT % {"key": key, "value": value.value}
        return sort
