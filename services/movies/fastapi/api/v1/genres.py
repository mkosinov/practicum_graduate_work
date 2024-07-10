from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Request

from core.enum import (
    APIGenreByUUIDDescription,
    APIGenreMainDescription,
    ErrorMessage,
)
from core.service import CommonService
from models.genre import GenreShort
from services.genre import get_genre_service

router = APIRouter()


@router.get(
    "/{genre_uuid}",
    response_model=GenreShort,
    summary=APIGenreByUUIDDescription.summary,
    description=APIGenreByUUIDDescription.description,
    response_description=APIGenreByUUIDDescription.response_description,
)
async def genre_details(
    request: Request,
    genre_uuid: UUID = Path(description="uuid жанра"),
    service: CommonService = Depends(get_genre_service),
) -> GenreShort | None:
    """
    Выдает информацию из elasticsearch (или из кэша redis)
    по указанному информацию по конкретному жанру

    :param genre_uuid: uuid жанра
    """
    genre = await service.get_by_uuid(uuid=genre_uuid, request=request)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.genre_not_found,
        )
    return genre


@router.get(
    "/",
    response_model=list[GenreShort],
    summary=APIGenreMainDescription.summary,
    description=APIGenreMainDescription.description,
    response_description=APIGenreMainDescription.response_description,
)
async def genre_list(
    request: Request,
    service: CommonService = Depends(get_genre_service),
) -> list[GenreShort] | None:
    """
    Выдает список всех жанров из elasticsearch (или из кэша redis)

    """
    genres = await service.get_list(
        request=request,
    )
    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.genres_not_found,
        )
    return genres
