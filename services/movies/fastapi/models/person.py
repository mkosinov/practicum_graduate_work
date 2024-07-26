from core.models import Base


class PersonShort(Base):
    """Короткая модель без кинопроизведений для показа в фильме по UUID."""

    full_name: str | None = ""


class InnerPersonFilmsShort(Base):
    """Короткая модель для показа в поиске по персонам."""

    roles: str | None = ""


class InnerPersonFilmsByUUID(Base):
    """Mодель фильма для показа в фильмах по UUID персоны."""

    title: str | None = ""
    imdb_rating: float | None = 0


class InnerPersonFilmsFull(InnerPersonFilmsShort):
    """Полнапя модель фильма."""

    title: str | None = ""
    imdb_rating: float | None = 0


class PersonFilms(PersonShort):
    """Модель для показа в поиске по персонам и по персоны по UUID."""

    films: list[InnerPersonFilmsShort] | None


class PersonFIlmsByUUID(PersonShort):
    """Mодель для показа в фильмах по UUID персоны."""

    films: list[InnerPersonFilmsByUUID] | None


class Person(PersonShort):
    """Полная модель персоны."""

    films: list[InnerPersonFilmsFull] | None
