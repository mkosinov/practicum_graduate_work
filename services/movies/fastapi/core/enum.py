from enum import Enum


class IndexName(str, Enum):
    """Модель названий индексов в Elasticsearch."""

    genre = "genres"
    movies = "movies"
    persons = "persons"


class PersonRoles(list, Enum):
    """Модель возможных названий ролей в Elasticsearch"""

    # Здесь надо разобраться что происходит
    # actors = "actors"
    # directors = "directors"
    # writers = "writers"
    roles = ["actors", "directors", "writers"]


class APIFilmByUUIDDescription(str, Enum):
    """Модель описания запроса фильма по UUID"""

    summary = "Информация о кинопроизведении"
    description = "Детальная информация о кинопроизведении по его UUID"
    response_description = "Описание кинопроизведения"


class APIFilmSearchDescription(str, Enum):
    """Модель описания запроса поиска фильма по имени."""

    summary = "Поиск по кинопроизведениям"
    description = "Поиск кинопроизведений"
    response_description = "Список всех кинопроизведений"


class APIFilmMainDescription(str, Enum):
    """Модель описания запроса поиска фильма для главной страницы."""

    summary = "Все кинопроизведения"
    description = "Все кинопроизведения с сортировкой и пагинацией"
    response_description = "Список кинопроизведений"


class APIGenreByUUIDDescription(str, Enum):
    """Модель описания запроса жанра по UUID"""

    summary = "Информация о жанре"
    description = "Детальная информация о жанре по его uuid"
    response_description = "Возвращает информацию о жанре"


class APIGenreMainDescription(str, Enum):
    """Модель описания запроса выдачи списка жанров."""

    summary = "Все жанры"
    description = "Каталог жанров"
    response_description = "Список всех жанров"


class APICommonDescription(str, Enum):
    """Модель описания общих полей-параметров к энпоинтам API."""

    page_number = "Номер страницы"
    page_size = "Количество результатов на странице"
    query = "Строка запроса для поиска по наименованию"
    sort = "Поле сортировки (например, -name)"


class APIPersonByUUIDDescription(str, Enum):
    """Модель описания запроса персон по UUID"""

    summary = "Данные по персоне"
    description = "Детальная информация о персоне по его uuid"
    response_description = (
        "Информация о персоне и список фильмов с ее участием"
    )


class APIPersonSearchDescription(str, Enum):
    """Модель описания запроса поиска персон по имени."""

    summary = "Все персоны"
    description = "Каталог персон"
    response_description = "Список всех персон"


class APIPersonFilmsByUUID(str, Enum):
    """Модель описания запроса поиска фильмов с участием персоны по UUID."""

    summary = "Фильмы по персоне"
    description = "Все фильмы, в съемке которых участвовал человек"
    response_description = "Краткая информация по фильмам"


class ErrorMessage(str, Enum):
    """Модель ответов, отдаваемых при ошибке."""

    film_not_found = "Кинопроизведение не найдено"
    films_not_found = "Кинопроизведения не найдены"
    genre_not_found = "Жанр не найден"
    genres_not_found = "Жанры не найдены"
    person_not_found = "Персона не найдена"
    persons_not_found = "Персоны не найдены"

    def __str__(self) -> str:
        return str.__str__(self)
