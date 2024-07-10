from core.models import Base


class GenreShort(Base):
    """Короткая модель ответа API по жанру."""

    name: str | None


class Genre(GenreShort):
    description: str | None
