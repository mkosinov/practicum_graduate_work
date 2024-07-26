from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName
from functional.testdata.film_data import get_films_to_load

INDEX_NAME = IndexName.MOVIES.value


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"query": "", "page_size": 100},
            {"found": 90, "status": HTTPStatus.OK},
        ),
        (
            {"query": "Star Wars: Episode", "page_size": 100},
            {"found": 80, "status": HTTPStatus.OK},
        ),
        (
            {"query": "Star", "page_size": 100},
            {"found": 80, "status": HTTPStatus.OK},
        ),
        (
            {"query": "Episode", "page_size": 100},
            {"found": 50, "status": HTTPStatus.OK},
        ),
        (
            {"query": "Non-existent title", "page_size": 100},
            {"found": 0, "status": HTTPStatus.NOT_FOUND},
        ),
        (
            {"query": "Sta", "page_size": 100},
            {"found": 0, "status": HTTPStatus.NOT_FOUND},
        ),
    ],
)
async def test_film_search_count(
    es_load, make_get_request, params, expected_response
):
    """Проверяем правильность количества найденных фильмов."""

    film_data_in = [
        *get_films_to_load(50, title="Star Wars: Episode IV - A New Hope"),
        *get_films_to_load(30, title="The Star"),
        *get_films_to_load(10, title="The Sun"),
    ]
    endpoint = "/api/v1/films/search"

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response["status"] == expected_response["status"]

    if response["status"] == HTTPStatus.OK:
        assert len(response["body"]) == expected_response["found"]
    else:
        assert len(response["body"]) == 1
        assert "detail" in response["body"]


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"query": "Sun"},
            {"status": HTTPStatus.OK},
        ),
        (
            {"query": "Non-existent title"},
            {"status": HTTPStatus.NOT_FOUND},
        ),
    ],
)
async def test_film_search_fields(
    es_load, make_get_request, params, expected_response
):
    """Проверяем правильность и полноту возврата данных."""

    film_data_in = [
        *get_films_to_load(50, title="Star Wars: Episode IV - A New Hope"),
        *get_films_to_load(30, title="The Star"),
        *get_films_to_load(10, title="The Sun"),
    ]
    endpoint = "/api/v1/films/search"

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response["status"] == expected_response["status"]
    if response["status"] == HTTPStatus.OK:
        assert all(
            [
                set(fields) == {"uuid", "title", "imdb_rating"}
                for fields in response["body"]
            ]
        )
        assert response["body"][0]["title"] == "The Sun"
        assert response["body"][0]["imdb_rating"] == 8.6

    else:
        assert len(response["body"]) == 1
        assert "detail" in response["body"]


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
async def test_film_search_pagination(
    es_load, make_get_request, page_params, expected_response
):
    """Проверяем параметры пагинации."""

    film_data_in = [
        *get_films_to_load(10, title="Star Wars: Episode IV - A New Hope"),
        *get_films_to_load(20, title="The Star"),
        *get_films_to_load(75, title="The Sun"),
    ]
    endpoint = "/api/v1/films/search"
    params = page_params | {"query": "Sun"}

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert response["status"] == expected_response["status"]
    assert len(response["body"]) == expected_response["length"]


async def test_film_search_cache(
    es_load,
    make_get_request,
    redis_client: Redis,
):
    """Проверяем работу кэша."""

    number = 75
    film_data_in = get_films_to_load(
        number, title="Star Wars: Episode IV - A New Hope"
    )
    endpoint = "/api/v1/films/search"
    page_number = 2
    page_size = 50
    params = {
        "query": "Star",
        "page_number": page_number,
        "page_size": page_size,
    }
    length_films = number - page_size

    # 1) Загружаем данные в эластик
    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)

    assert len(response["body"]) == length_films

    # 2) Подгружаем еще фильмы и отправляем запрос с теми же параметрами
    add_number = 10
    film_data_in = get_films_to_load(add_number, title="The Star")

    await es_load(INDEX_NAME, film_data_in)
    response = await make_get_request(endpoint, params)
    # Проверяем, что кэш работает - вернулось старое количество фильмов из кэша
    assert len(response["body"]) == length_films

    # 3) Сбрасываем кэш. Теперь возвращается количество с учетом добавленных фильмов
    await redis_client.flushall()
    response = await make_get_request(endpoint, params)

    assert len(response["body"]) == length_films + add_number
