"""Тесты эндпоинта /api/v1/persons/{person_uuid}"""
from http import HTTPStatus

import pytest
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from functional.settings import IndexName, index_settings
from functional.testdata.person_answer_data import person_by_uuid
from functional.testdata.person_data import persons_to_load

INDEX_NAME = IndexName.PERSONS.value
ENDPOINT = "/api/v1/persons/"


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
async def test_person_details(
    es_load,
    make_get_request,
    person_uuid,
    expected_response,
):
    """Проверка поиска по UUID персоны."""
    endpoint = f"{ENDPOINT}{person_uuid['uuid']}"
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]


@pytest.mark.parametrize(
    "person_uuid, expected_response",
    [
        (
            {"uuid": persons_to_load[1]["uuid"]},
            {"body": person_by_uuid},
        ),
    ],
)
async def test_person_by_uuid_answer(
    es_load,
    make_get_request,
    person_uuid,
    expected_response,
):
    """Проверка соответствия ответа по UUID персоны."""
    endpoint = f"{ENDPOINT}{person_uuid['uuid']}"
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(endpoint)
    assert response["body"] == expected_response["body"]


async def test_person_by_uuid_redis(
    es_load,
    make_get_request,
    es_client: AsyncElasticsearch,
    redis_client: Redis,
):
    """Проверка работы redis в эндпоинте."""
    endpoint = f"{ENDPOINT}{persons_to_load[0]['uuid']}"
    # Загружаем в эластик фильмы c персонами.
    await es_load(INDEX_NAME, persons_to_load)
    response = await make_get_request(endpoint)
    # Проверяем ответ и сохраняем в кэш.
    assert response["status"] == HTTPStatus.OK
    # Очищаем индекс эластик.
    await es_client.indices.delete(index=INDEX_NAME)
    await es_client.indices.create(
        index=INDEX_NAME,
        mappings=index_settings.MAPPINGS[INDEX_NAME],
        settings=index_settings.SETTINGS,
    )
    # Проверяем что ответ после отчистки индекса находит персону
    response = await make_get_request(endpoint)
    assert response["status"] == HTTPStatus.OK
    # Сбрасываем кэш. Теперь индекс и кэш пуст
    await redis_client.flushall()
    # Проверяем ответ после отчистки индекса и кэша.
    response = await make_get_request(endpoint)
    assert response["status"] == HTTPStatus.NOT_FOUND
