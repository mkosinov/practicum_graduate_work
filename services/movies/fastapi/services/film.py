from functools import lru_cache
from pprint import pprint

from core.cache import AbstractCacheService, get_cache_service
from core.config import settings
from core.enum import IndexName
from core.service import CommonService
from core.storage import ElasticService, get_storage_service
from models.film import Film
from pydantic import BaseModel

from fastapi import Depends, Request


class FilmService(CommonService):
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
        sort: str = "-imdb_rating",
        search_query: dict = None,
        bool_operator: str = "must",
        request: Request = None,
    ) -> list[Film]:
        """Расширенный метод поиска по кинопроизведениям с учетом всех полей индекса

        :param page_number: Номер страницы (начиная с 1).
        :param page_size: Количество элементов на странице.
        :param sort: Поле по которому производится сортировка.
        :param search_query: Словарь с параметрами поиска.

        search_query = {
            "movie": {
                "title": str,
                "description": str,
                "imdb_rating": float,
                "creation_date": str,
                "subscribers_only": bool,
            },
            "genres": [{"name": str}],
            "persons": [{"full_name": str, "role": str}],
        }
        """
        print("\n")
        pprint(search_query)
        if list_instances := await self.cache.get_instances_from_cache(
            request=request, model=self.model
        ):
            return list_instances
        if sort:
            sort = self._get_sort(sort=sort)
        matches = search_query.get("movie", {})
        nested_matches = {
            "genre.name": genre.get("name", "")
            for genre in search_query.get("genres", [])
        }

        for person in search_query.get("persons", []):
            if person.get("role", "") == "actor":
                nested_matches = {
                    "actors.full_name": person.get("full_name", "")
                }
            elif person.get("role", "") == "writer":
                nested_matches = {
                    "writers.full_name": person.get("full_name", "")
                }
            elif person.get("role", "") == "director":
                nested_matches = {
                    "directors.full_name": person.get("full_name", "")
                }
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
        if list_instances and request:
            await self.cache.put_instances_to_cache(
                request=request, instances=list_instances
            )
        return list_instances


@lru_cache()
def get_film_service(
    cache=Depends(get_cache_service),
    elastic=Depends(get_storage_service),
) -> FilmService:
    return FilmService(
        cache=cache, elastic=elastic, model=Film, index=IndexName.movies
    )
