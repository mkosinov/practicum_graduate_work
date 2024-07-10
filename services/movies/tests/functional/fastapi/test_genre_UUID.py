from http import HTTPStatus

import pytest

from functional.settings import IndexName
from functional.testdata.genre_data import genre_test_data, genre_test_modify


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"},
            {
                "status": HTTPStatus.OK,
                "body": {
                    "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                    "name": "Action",
                },
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_genre_get_by_uuid_elastic(
    es_load, make_get_request, query_data, expected_response
):
    """Тест выдачи жанра по UUID"""
    await es_load(IndexName.GENRES.value, genre_test_data)
    endpoint = f'/api/v1/genres/{query_data["uuid"]}'
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]
    assert response["body"] == expected_response["body"]


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"uuid": "incorrect uuid"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY},
        ),
        (
            {"uuid": "00000000-0000-0000-0000-000000000000"},
            {
                "status": HTTPStatus.NOT_FOUND,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_genre_get_by_uuid_validations(
    es_load, make_get_request, query_data, expected_response
):
    """Тест выдачи жанра по UUID"""
    await es_load(IndexName.GENRES.value, genre_test_data)
    endpoint = f'/api/v1/genres/{query_data["uuid"]}'
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]


@pytest.mark.parametrize(
    "query_data, expected_response",
    [
        (
            {"uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"},
            {
                "status": HTTPStatus.OK,
                "body_init_value": {
                    "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                    "name": "Action",
                },
                "body_new_value": {
                    "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff",
                    "name": "New value",
                },
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_genre_get_by_uuid_cache(
    es_load, make_get_request, redis_client, query_data, expected_response
):
    """Тест работы кэша"""
    endpoint = f'/api/v1/genres/{query_data["uuid"]}'

    # индексируем в elasticsearch тестовые данные и запрашиваем их (кэшируем)
    await es_load(IndexName.GENRES.value, genre_test_data)
    response = await make_get_request(endpoint)

    # индексируем в elasticsearch скорректированные тестовые данные
    await es_load(IndexName.GENRES.value, genre_test_modify)

    # запрашиваем тестовые данные и проверяем, что вернулись исходные тестовые данные (до корректировки)
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]
    assert response["body"] == expected_response["body_init_value"]

    # сбрасываем кэш для проверки индексации скорректированных тестовых данных
    await redis_client.flushall()
    response = await make_get_request(endpoint)
    assert response["status"] == expected_response["status"]
    assert response["body"] == expected_response["body_new_value"]
