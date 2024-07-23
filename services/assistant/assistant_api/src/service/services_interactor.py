from functools import lru_cache

from interface.movies_api import (FilmResponse, MoviesApiInterface,
                                  PersonResponse, get_movies_api_interface)


class ServicesInteractor:
    def __init__(self, movies_api_interface: MoviesApiInterface):
        self.movies_api = movies_api_interface

    async def search_films(self, slots: dict) -> FilmResponse | None:
        return await self.movies_api.search_films(slots)

    async def search_persons(self, slots: dict) -> PersonResponse | None:
        return await self.movies_api.search_persons(slots)
    

@lru_cache()
def get_service_interactor() -> ServicesInteractor:
    return ServicesInteractor(movies_api_interface=get_movies_api_interface())