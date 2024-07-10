from http import HTTPStatus
from uuid import UUID

from core.config import settings
from core.enum import (
    APICommonDescription,
    APIFilmByUUIDDescription,
    APIFilmMainDescription,
    APIFilmSearchDescription,
    ErrorMessage,
)
from core.service import CommonService
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from models.film import Film, FilmShort
from services.film import get_film_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[FilmShort],
    summary=APIFilmSearchDescription.summary,
    description=APIFilmSearchDescription.description,
    response_description=APIFilmSearchDescription.response_description,
)
async def film_short_list(
    request: Request,
    query: str = Query(None, description=APICommonDescription.query),
    page_number: int = Query(
        1, description=APICommonDescription.page_number, ge=1
    ),
    page_size: int = Query(
        settings.STANDART_PAGE_SIZE,
        description=APICommonDescription.page_size,
        ge=1,
    ),
    service: CommonService = Depends(get_film_service),
) -> list[FilmShort]:
    """
    Поиск кинопроизведений с использованием Elasticsearch (или кеша Redis).

    :param query: Строка запроса для поиска фильмов.
    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    """
    matches = {"title": query} if query else None
    films = await service.get_list(
        page_number=page_number,
        page_size=page_size,
        matches=matches,
        bool_operator="must",
        request=request,
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.films_not_found,
        )
    return films


@router.get(
    "/{uuid}",
    response_model=Film,
    summary=APIFilmByUUIDDescription.summary,
    description=APIFilmByUUIDDescription.description,
    response_description=APIFilmByUUIDDescription.response_description,
)
async def film_details(
    request: Request,
    uuid: UUID = Path(description="uuid кинопроизведения"),
    service: CommonService = Depends(get_film_service),
) -> Film:
    """
    Выдает информацию из elasticsearch (или из кэша redis) о кинопроизведении
    по uuid кинопроизведения.
    """
    film: Film = await service.get_by_uuid(uuid=uuid, request=request)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.film_not_found,
        )
    return film


@router.get(
    "",
    response_model=list[FilmShort],
    summary=APIFilmMainDescription.summary,
    description=APIFilmMainDescription.description,
    response_description=APIFilmMainDescription.response_description,
)
async def film_list(
    request: Request,
    page_number: int = Query(
        1, description=APICommonDescription.page_number, ge=1
    ),
    page_size: int = Query(
        settings.STANDART_PAGE_SIZE,
        description=APICommonDescription.page_size,
        ge=1,
    ),
    sort: str = Query("-imdb_rating", description=APICommonDescription.sort),
    genre_uuid: UUID = Query(
        None, description="Фильтр фильмов по uuid жанра", alias="genre"
    ),
    service: CommonService = Depends(get_film_service),
) -> list[FilmShort]:
    """
    Поиск кинопроизведений с использованием Elasticsearch (или кеша Redis).

    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    :param sort: Поле для сортировки (например, imdb_rating).
    :param genre: Фильтр фильмов по id жанра.
    """
    nested_matches = {"genre.uuid": genre_uuid} if genre_uuid else None
    films = await service.get_list(
        page_number=page_number,
        page_size=page_size,
        sort=sort,
        nested_matches=nested_matches,
        bool_operator="must",
        request=request,
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.films_not_found,
        )

    return films
