from functools import lru_cache

import backoff
from httpx import NetworkError, TimeoutException
from opentelemetry import trace

from interface.movies_api import (
    FilmResponse,
    MoviesApiInterface,
    PersonResponse,
    get_movies_api_interface,
)

tracer = trace.get_tracer(__name__)


class ServicesInteractor:
    def __init__(self, movies_api_interface: MoviesApiInterface):
        self.movies_api = movies_api_interface

    @backoff.on_exception(
        backoff.expo, (TimeoutException, NetworkError), max_time=1, max_tries=3
    )
    @tracer.start_as_current_span("servicer_interactor.search_films")
    async def search_films(self, slots: dict) -> FilmResponse | None:
        return await self.movies_api.search_films(slots)

    @backoff.on_exception(
        backoff.expo, (TimeoutException, NetworkError), max_time=1, max_tries=3
    )
    @tracer.start_as_current_span("servicer_interactor.search_persons")
    async def search_persons(self, slots: dict) -> PersonResponse | None:
        return await self.movies_api.search_persons(slots)


@lru_cache()
def get_service_interactor() -> ServicesInteractor:
    return ServicesInteractor(movies_api_interface=get_movies_api_interface())
