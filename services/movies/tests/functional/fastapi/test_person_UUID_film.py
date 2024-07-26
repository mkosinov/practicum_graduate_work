"""Тесты эндпоинта /api/v1/persons/{person_uuid}/film"""
from http import HTTPStatus

import pytest
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from functional.settings import IndexName, index_settings
from functional.testdata.person_answer_data import person_uuid_film
from functional.testdata.person_data import persons_to_load

index_name = IndexName.PERSONS.value
ENDPOINT = "/api/v1/persons/%s/film"


@pytest.mark.parametrize(
    "person_uuid, expected_response",
    [
        (
            {"uuid": persons_to_load[0]["uuid"]},
            {"status": HTTPStatus.OK},
        ),
        (
            {"uuid": "00000000-0000-0000-0000-000000000000"},
            {"status": HTTPStatus.NOT_FOUND},
        ),
    ],
)
async def test_films_by_person_UUID_details(
    es_load,
    make_get_request,
    person_uuid,
    expected_response,
):
    """Проверка поиска фильмов по UUID персоны."""
    endpoint = ENDPOINT % (person_uuid["uuid"])
    await es_load(index_name, persons_to_load)
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]


@pytest.mark.parametrize(
    "person_uuid, expected_response",
    [
        (
            {"uuid": persons_to_load[1]["uuid"]},
            {"body": person_uuid_film},
        ),
    ],
)
async def test_films_by_person_UUID_answer(
    es_load,
    make_get_request,
    person_uuid,
    expected_response,
):
    """Проверка соответствия ответа фильмов по UUID персоны."""
    endpoint = ENDPOINT % (person_uuid["uuid"])
    await es_load(index_name, persons_to_load)
    response = await make_get_request(endpoint)
    assert response["body"] == expected_response["body"]


async def test_films_by_person_redis(
    es_load,
    make_get_request,
    es_client: AsyncElasticsearch,
    redis_client: Redis,
):
    """Проверка работы redis в эндпоинте."""
    endpoint = ENDPOINT % (persons_to_load[1]["uuid"])

    # Загружаем в эластик фильмы c персонами.
    await es_load(index_name, persons_to_load)
    response = await make_get_request(endpoint)
    # Проверяем ответ и сохраняем в кэш.
    assert response["status"] == HTTPStatus.OK
    # Очищаем индекс эластик.
    await es_client.indices.delete(index=index_name)
    await es_client.indices.create(
        index=index_name,
        mappings=index_settings.MAPPINGS[index_name],
        settings=index_settings.SETTINGS,
    )
    # Проверяем что ответ после отчистки индекса находит фильмы по персоне
    response = await make_get_request(endpoint)
    assert response["status"] == HTTPStatus.OK
    # Сбрасываем кэш. Теперь индекс и кэш пуст
    await redis_client.flushall()
    # Проверяем ответ после отчистки индекса и кэша.
    response = await make_get_request(endpoint)
    assert response["status"] == HTTPStatus.NOT_FOUND
