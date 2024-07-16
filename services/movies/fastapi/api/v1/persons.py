from http import HTTPStatus
from uuid import UUID

from core.config import settings
from core.enum import (
    APICommonDescription,
    APIPersonAdvancedSearchDescription,
    APIPersonByUUIDDescription,
    APIPersonFilmsByUUID,
    APIPersonSearchDescription,
    ErrorMessage,
)
from core.service import CommonService
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
)
from models.person import InnerPersonFilmsByUUID, Person, PersonFilms
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[PersonFilms],
    summary=APIPersonSearchDescription.summary,
    description=APIPersonSearchDescription.description,
    response_description=APIPersonSearchDescription.response_description,
)
async def person_search(
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
    service: CommonService = Depends(get_person_service),
) -> list[PersonFilms]:
    """
    Поиск по персонам в elasticsearch (или кэша Redis):

    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    :param query: Строка для поиска по имени персоны
    """
    matches = {"full_name": query} if query else None
    persons = await service.get_list(
        matches=matches,
        request=request,
        page_number=page_number,
        page_size=page_size,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.persons_not_found,
        )
    return persons


@router.get(
    "/{uuid}",
    response_model=PersonFilms,
    summary=APIPersonByUUIDDescription.summary,
    description=APIPersonByUUIDDescription.description,
    response_description=APIPersonByUUIDDescription.response_description,
)
async def person_details(
    request: Request,
    uuid: UUID = Path(description="uuid персоны"),
    service: CommonService = Depends(get_person_service),
) -> PersonFilms:
    person = await service.get_by_uuid(uuid=uuid, request=request)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.person_not_found,
        )
    return person


@router.get(
    "/{uuid}/film",
    response_model=list[InnerPersonFilmsByUUID],
    summary=APIPersonFilmsByUUID.summary,
    description=APIPersonFilmsByUUID.description,
    response_description=APIPersonFilmsByUUID.response_description,
)
async def person_films(
    request: Request,
    uuid: UUID = Path(description="uuid персоны"),
    service: CommonService = Depends(get_person_service),
) -> list[InnerPersonFilmsByUUID] | None:
    person = await service.get_by_uuid(uuid=uuid, request=request)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.films_not_found,
        )
    return person.films


@router.post(
    "/advanced_search",
    response_model=list[Person],
    summary=APIPersonAdvancedSearchDescription.summary,
    description=APIPersonAdvancedSearchDescription.description,
    response_description=APIPersonAdvancedSearchDescription.response_description,
)
async def advanced_search_persons(
    request: Request,
    page_number: int = Query(
        1, description=APICommonDescription.page_number, ge=1
    ),
    page_size: int = Query(
        1,
        description=APICommonDescription.page_size,
        ge=1,
    ),
    search_query: dict = Body(
        None,
        examples=[
            {
                "person": {
                    "full_name": "Lucas",
                },
                "films": {
                    "title": "war",
                    "roles": "director",
                },
            },
            {
                "person": {
                    "full_name": "Lucas",
                },
                "films": {
                    "title": "star war",
                    "description": "jedi",
                    "imdb_rating": 0.0,
                    "creation_date": "",
                    "roles": "director",
                },
            },
        ],
        description="field:value dict",
    ),
    service: PersonService = Depends(get_person_service),
) -> list[Person]:
    """
    Поиск кинопроизведений с использованием Elasticsearch (или кеша Redis).

    :param search_query: Словарь с полями и значениями, которые нужно использовать для поиска.
    :param page_number: Номер страницы (начиная с 1).
    :param page_size: Количество элементов на странице.
    """
    persons = await service.advanced_search(
        page_number=page_number,
        page_size=page_size,
        search_query=search_query,
        bool_operator="must",
        request=request,
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=ErrorMessage.films_not_found,
        )
    return persons
