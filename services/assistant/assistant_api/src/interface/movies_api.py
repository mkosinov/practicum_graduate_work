from datetime import date

import httpx
from core.settings import get_settings
from pydantic import BaseModel, ConfigDict

search_films_structure = {
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

search_persons_structure = {
    "person": {"full_name": str},
    "films": [
        {
            "title": str,
            "description": str,
            "imdb_rating": float,
            "creation_date": str,
            "roles": str,
        }
    ],
}


class MovieSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = None
    description: str | None = None
    imdb_rating: float | None = None
    creation_date: str | None = None
    subscribers_only: bool | None = None


class GenreSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None = None


class PersonSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    full_name: str | None = None
    role: str | None = None


class SearchFilmsSchema(BaseModel):
    movie: MovieSchema = MovieSchema()
    genres: list[GenreSchema] = []
    persons: list[PersonSchema] = []
    """
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


class GenreInnerResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str | None


class PersonInnerResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    full_name: str | None = ""


class FilmResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = ""
    imdb_rating: float | None = 0.0
    genre: list[GenreInnerResponse] | None = []
    description: str | None = ""
    creation_date: date | None
    actors: list[PersonInnerResponse] | None = []
    writers: list[PersonInnerResponse] | None = []
    directors: list[PersonInnerResponse] | None = []
    subscribers_only: bool | None = False


class PersonFilms(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str | None = None
    imdb_rating: float | None = 0.0
    creation_date: date | None = None
    roles: str | None = None


class PersonResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    full_name: str | None = None
    films: list[PersonFilms] | None = None


class MoviesApiInterface:
    def create_film_query_dict(self, slots: dict, structure: dict) -> dict:
        search_query = {}
        search_query = {"movie": {}, "genres": [], "persons": []}
        for key, value in slots.items():
            if key in structure.get("movie").keys():
                search_query["movie"][key] = value.get("value", "")
            elif key in structure.get("genres")[0].keys():
                search_query["genres"].append({key: value.get("value", "")})
            elif key in structure.get("persons")[0].keys():
                search_query["persons"].append({key: value.get("value", "")})
        return search_query

    def create_person_query_dict(self, slots: dict, structure: dict) -> dict:
        search_query = {}
        search_query = {"person": {}, "films": []}
        for key, value in slots.items():
            if key in structure.get("person").keys():
                search_query["person"][key] = value.get("value", "")
            elif key in structure.get("films")[0].keys():
                search_query["films"].append({key: value.get("value", "")})
        search_query["films"].append(
            {"roles": slots.get("role", {}).get("value", "")}
        )
        return search_query

    async def search_films(self, slots: dict) -> FilmResponse | None:
        search_query = self.create_film_query_dict(
            slots, search_films_structure
        )
        response = httpx.post(
            get_settings().movies_api_url + "/films/advanced_search",
            json=search_query,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return FilmResponse.model_validate(response.json()[0])
        else:
            return None

    async def search_persons(self, slots: dict) -> FilmResponse | None:
        search_query = self.create_person_query_dict(
            slots, search_persons_structure
        )
        response = httpx.post(
            get_settings().movies_api_url + "/persons/advanced_search",
            json=search_query,
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            return PersonResponse.model_validate(response.json()[0])
        else:
            return None


def get_movies_api_interface():
    return MoviesApiInterface()
