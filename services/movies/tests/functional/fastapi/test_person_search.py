"""Тесты эндпоинта /api/v1/persons/search"""
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from functional.settings import IndexName
from functional.testdata.person_answer_data import person_all, person_by_uuid
from functional.testdata.person_data import persons_to_load

INDEX_NAME = IndexName.PERSONS.value
ENDPOINT = "/api/v1/persons/search"


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"query": "Arnaz"},
            {"status": HTTPStatus.OK},
        ),
        (
            {"query": "bobr"},
            {"status": HTTPStatus.NOT_FOUND},
        ),
    ],
)
async def test_person_search_query(
    es_load,
    make_get_request,
    params,
    expected_response,
):
    """Проверка поиска имени персоны."""
    await es_load(INDEX_NAME, persons_to_load)
    params = {"query": params["query"]}
    response = await make_get_request(ENDPOINT, params)
    assert response["status"] == expected_response["status"]


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"page_size": 2, "page_number": 1},
            {"status": HTTPStatus.OK},
        ),
        (
            {"page_size": 2, "page_number": 2},
            {"status": HTTPStatus.NOT_FOUND},
        ),
        (
            {"page_size": 1, "page_number": 2},
            {"status": HTTPStatus.OK},
        ),
    ],
)
async def test_person_search_paginator(
    es_load,
    make_get_request,
    params,
    expected_response,
):
    """Проверка работы пагинатора персон."""

    await es_load(INDEX_NAME, persons_to_load)
    params = {
        "page_size": params["page_size"],
        "page_number": params["page_number"],
    }
    response = await make_get_request(ENDPOINT, params)
    assert response["status"] == expected_response["status"]


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"query": "Arnaz"},
            {"body": person_by_uuid},
        ),
    ],
)
async def test_person_search_answer(
    es_load,
    make_get_request,
    params,
    expected_response,
):
    """Проверка соответствия ответа персоны."""
    params = {"query": params["query"]}
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(ENDPOINT, params)
    assert response["body"][0] == expected_response["body"]


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"page_size": 2, "page_number": 1},
            {"body": person_all},
        ),
        (
            {"page_size": 1, "page_number": 1},
            {"body": [person_all[0]]},
        ),
        (
            {"page_size": 1, "page_number": 2},
            {"body": [person_all[1]]},
        ),
    ],
)
async def test_person_search_paginator_answer(
    es_load,
    make_get_request,
    params,
    expected_response,
):
    """Проверка ответа пагинатора."""
    params = {
        "page_size": params["page_size"],
        "page_number": params["page_number"],
    }
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(ENDPOINT, params)
    assert response["body"] == expected_response["body"]


@pytest.mark.parametrize(
    "params, expected_response",
    [
        (
            {"page_size": 1},
            {"count": 1},
        ),
        (
            {"page_size": 2},
            {"count": 2},
        ),
    ],
)
async def test_person_search_paginator_count(
    es_load,
    make_get_request,
    params,
    expected_response,
):
    """Проверка количества в ответе пагинатора."""
    params = {"page_size": params["page_size"]}
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(ENDPOINT, params)
    assert len(response["body"]) == expected_response["count"]


async def test_person_search_redis(
    es_load, make_get_request, redis_client: Redis
):
    """Проверка работы redis в эндпоинте."""

    # Загружаем в эластик один фильм с 2-мя персонами.
    await es_load(INDEX_NAME, [persons_to_load[0]])
    response = await make_get_request(ENDPOINT)
    # Проверяем что ответ API содержит одну персону.
    assert len(response["body"]) == 1
    # Загружаем в эластик еще один фильм с новой песоной.
    await es_load(INDEX_NAME, [persons_to_load[1]])
    response = await make_get_request(ENDPOINT)
    # Проверяем что ответ API содержит 1 персону, т.к. из кэша
    assert len(response["body"]) == 1
    # Сбрасываем кэш. Теперь возвращаются 2 персоны из эластика
    await redis_client.flushall()
    response = await make_get_request(ENDPOINT)
    # Проверяем что ответ API содержит один фильм, т.к. из кэша
    assert len(response["body"]) == 2
