from functools import lru_cache
from pprint import pprint

from core.cache import AbstractCacheService, get_cache_service
from core.config import settings
from core.enum import IndexName
from core.service import CommonService
from core.storage import ElasticService, get_storage_service
from models.person import Person
from pydantic import BaseModel

from fastapi import Depends, Request


class PersonService(CommonService):
    def __init__(
        self,
        cache: AbstractCacheService,
        elastic: ElasticService,
        model: BaseModel,
        index: str,
    ):
        super().__init__(cache, elastic, model, index)

    async def advanced_search(
        self,
        page_number: int = 1,
        page_size: int = settings.STANDART_PAGE_SIZE,
        search_query: dict = None,
        bool_operator: str = "must",
        request: Request = None,
    ) -> list[Person]:
        """Расширенный метод поиска по персонам с учетом всех полей индекса

        :param page_number: Номер страницы (начиная с 1).
        :param page_size: Количество элементов на странице.
        :param search_query: Словарь с параметрами поиска.

        search_query = {
            "person": {
                "full_name": str,
            },
            "films": [
                {
                    "title": str,
                    "description": str,
                    "imdb_rating": float,
                    "creation_date": str,
                    "roles": str
                }
            ],
        }
        """
        print("\n")
        pprint(search_query)
        matches = search_query.get("person", {})
        nested_matches = {}
        films: list[dict] = search_query.get("films", [])
        for film in films:
            for key, value in film.items():
                nested_matches["films." + key] = value

        es_query = self._get_es_query(
            page_number=page_number,
            page_size=page_size,
            matches=matches,
            nested_matches=nested_matches,
            bool_operator=bool_operator,
        )
        list_instances = await self.elastic.get_list_by_search(
            index=self.index, model_class=self.model, query=es_query
        )
        if list_instances and request:
            await self.cache.put_instances_to_cache(
                request=request, instances=list_instances
            )
        return list_instances


@lru_cache()
def get_person_service(
    cache=Depends(get_cache_service),
    elastic=Depends(get_storage_service),
) -> PersonService:
    return PersonService(
        cache=cache,
        elastic=elastic,
        model=Person,
        index=IndexName.persons,
    )
