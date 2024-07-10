from core.models import Base
from models.genre import GenreShort
from models.person import PersonShort


class FilmShort(Base):
    """Короткая модель ответа API по кинопроизведениям."""

    title: str | None = ""
    imdb_rating: float | None = 0


class Film(FilmShort):
    """Полная модель фильмов из индекса и для ответа АPI по UUID."""

    genre: list[GenreShort] | None = []
    description: str | None = ""
    actors: list[PersonShort] | None = []
    writers: list[PersonShort] | None = []
    directors: list[PersonShort] | None = []
    subscribers_only: bool | None = False
