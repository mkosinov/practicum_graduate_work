from pydantic import BaseModel


class AdvancedSearchFilmNestedGenre(BaseModel):
    title: str


class AdvancedSearchFilmNestedPerson(BaseModel):
    full_name: str
    role: str


class AdvancedSearchFilm(BaseModel):
    title: str | None
    description: str | None
    imdb_rating: float | None
    creation_date: str | None
    subscribers_only: bool | None
    genre: list[AdvancedSearchFilmNestedGenre] | list
    person: list[AdvancedSearchFilmNestedPerson] | list
