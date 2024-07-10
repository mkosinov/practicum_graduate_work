from http import HTTPStatus

import pytest
from functional.settings import IndexName
from functional.testdata.film_data import (
    FILM,
    GENRE_PARAM,
    film_to_load,
    get_films_to_load,
)
from redis.asyncio import Redis

INDEX_NAME = IndexName.MOVIES.value


async def test_film_list_fields(
    es_load,
    make_get_request,
):
    """Проверяем правильность и полноту возврата данных."""

    film_data_in = [v for v in film_to_load.values()]
    endpoint = "/api/v1/films"

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint)

    assert response["status"] == HTTPStatus.OK
    assert len(response["body"]) == len(film_data_in)
    assert all(
        [
            set(fields) == {"uuid", "title", "imdb_rating"}
            for fields in response["body"]
        ]
    )
    assert response["body"][2] == {
        "uuid": film_to_load["film1"]["uuid"],
        "title": film_to_load["film1"]["title"],
        "imdb_rating": film_to_load["film1"]["imdb_rating"],
    }


@pytest.mark.parametrize(
    "params, expected_order",
    [
        (
            {"sort": "-imdb_rating"},
            {
                "status": HTTPStatus.OK,
                "order": ["film2", "film5", "film1", "film3", "film4"],
            },
        ),
        (
            {"sort": "imdb_rating"},
            {
                "status": HTTPStatus.OK,
                "order": ["film4", "film3", "film1", "film5", "film2"],
            },
        ),
        (
            {"sort": "-imdb_rating", "genre": GENRE_PARAM["Action"]},
            {"status": HTTPStatus.OK, "order": ["film5", "film1", "film4"]},
        ),
        (
            {"sort": "imdb_rating", "genre": GENRE_PARAM["Action"]},
            {"status": HTTPStatus.OK, "order": ["film4", "film1", "film5"]},
        ),
        (
            {
                "sort": "imdb_rating",
                "genre": GENRE_PARAM["Non-existent Genre"],
            },
            {"status": HTTPStatus.NOT_FOUND, "order": None},
        ),
    ],
)
async def test_film_list_sort_genre(
    es_load, make_get_request, params, expected_order
):
    """Проверяем параметры сортировки и фильтрации по жанру."""

    film_data_in = [v for v in film_to_load.values()]
    endpoint = "/api/v1/films"

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response["status"] == expected_order["status"]
    received_order = (
        [FILM[f["uuid"]] for f in response["body"]]
        if response["status"] == HTTPStatus.OK
        else None
    )
    assert received_order == expected_order["order"]


@pytest.mark.parametrize(
    "page_params, expected_response",
    [
        (
            {"page_number": 1, "page_size": 1000},
            {"length": 75, "status": HTTPStatus.OK},
        ),
        (
            {"page_number": 1, "page_size": 50},
            {"length": 50, "status": HTTPStatus.OK},
        ),
        (
            {"page_number": 2, "page_size": 50},
            {"length": 75 - 50, "status": HTTPStatus.OK},
        ),
        (
            {"page_number": 3, "page_size": 50},
            {"length": 1, "status": HTTPStatus.NOT_FOUND},
        ),
        (
            {"page_number": 1, "page_size": -1},
            {"length": 1, "status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            {"page_number": -1, "page_size": 50},
            {"length": 1, "status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
    ],
)
async def test_film_list_pagination(
    es_load, make_get_request, page_params, expected_response
):
    """Проверяем параметры пагинации."""

    film_data_in = get_films_to_load(75)
    endpoint = "/api/v1/films"

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, page_params)

    assert response["status"] == expected_response["status"]
    assert len(response["body"]) == expected_response["length"]


async def test_film_list_cache(
    es_load,
    make_get_request,
    redis_client: Redis,
):
    """Проверяем работу кэша."""

    number = 75
    film_data_in = get_films_to_load(number)
    endpoint = "/api/v1/films"
    page_number = 2
    page_size = 50
    params = {"page_number": page_number, "page_size": page_size}
    length_films = number - page_size

    # 1) Загружаем данные в эластик 'film_title'
    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert len(response["body"]) == length_films

    # 2) Подгружаем еще фильмы и отправляем запрос с теми же параметрами
    add_number = 10
    film_data_in = get_films_to_load(add_number)

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)
    # Проверяем, что кэш работает - вернулось старое количество фильмов из кэша
    assert len(response["body"]) == length_films

    # 3) Сбрасываем кэш. Теперь возвращается количество с учетом добавленных фильмов
    await redis_client.flushall()
    response = await make_get_request(endpoint, params)

    assert len(response["body"]) == length_films + add_number
