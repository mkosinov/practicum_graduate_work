import json
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Base(BaseModel):
    """Абстрактная модель. Добавляет ID."""

    uuid: UUID

    class Config:
        orm_mode = True


class GenreShort(Base):
    name: str | None


class Genre(GenreShort):
    description: str | None

    @classmethod
    def transform_from_input(cls, data):
        (
            uuid,
            name,
            description,
        ) = data
        dm = cls(
            uuid=UUID(uuid),
            name=name,
            description=description if description else None,
        )
        return dm


class FilmToPersonIndex(Base):
    title: str | None
    imdb_rating: float | None = 0
    roles: str


class PersonShort(Base):
    full_name: str


class Person(PersonShort):
    films: list[FilmToPersonIndex] | None = []

    @classmethod
    def _deserialize_film(cls, film_data):
        return FilmToPersonIndex(
            uuid=UUID(film_data["uuid"]),
            title=film_data["title"],
            imdb_rating=film_data["imdb_rating"],
            roles=film_data["roles"],
        )

    @classmethod
    def _deserialize_film_list(cls, data_list):
        return [
            cls._deserialize_film(film)
            for film in data_list
            if isinstance(film, dict)
        ]

    @classmethod
    def transform_from_input(cls, data):
        (
            uuid,
            full_name,
            modified,
            films_data,
        ) = data
        dm = cls(
            uuid=UUID(uuid),
            full_name=full_name,
            films=cls._deserialize_film_list(json.loads(films_data)),
        )
        return dm


class Filmwork(Base):
    imdb_rating: float | None = 0
    genre: list[GenreShort] | None = []
    title: str | None
    description: str | None
    subscribers_only: bool | None = False
    actors: list[PersonShort] | None = []
    writers: list[PersonShort] | None = []
    directors: list[PersonShort] | None = []

    @classmethod
    def _deserialize_person(cls, person_data):
        return PersonShort(
            uuid=UUID(person_data["uuid"]),
            full_name=person_data["full_name"],
        )

    @classmethod
    def _deserialize_person_list(cls, data_list):
        return [
            cls._deserialize_person(person)
            for person in data_list
            if isinstance(person, dict)
        ]

    @classmethod
    def _deserialize_genre(cls, genre_data):
        return GenreShort(
            uuid=UUID(genre_data[0]),
            name=genre_data[1],
        )

    @classmethod
    def _deserialize_genres_dict(cls, data_dict):
        return [
            cls._deserialize_genre(genre)
            for genre in data_dict.items()
            if isinstance(genre, tuple)
        ]

    @classmethod
    def transform_from_input(cls, data):
        (
            uuid,
            imdb_rating,
            genres_data,
            title,
            description,
            subscribers_only,
            actors_data,
            writers_data,
            directors_data,
            modified,
        ) = data
        dm = cls(
            uuid=UUID(uuid),
            imdb_rating=float(imdb_rating) if imdb_rating else None,
            genre=cls._deserialize_genres_dict(genres_data),
            title=title,
            description=description,
            subscribers_only=subscribers_only,
            actors=cls._deserialize_person_list(json.loads(actors_data)),
            writers=cls._deserialize_person_list(json.loads(writers_data)),
            directors=cls._deserialize_person_list(json.loads(directors_data)),
        )
        return dm


class IndexName(str, Enum):
    """Модель названий индексов в Elasticsearch."""

    genres = "genres"
    movies = "movies"
    persons = "persons"
