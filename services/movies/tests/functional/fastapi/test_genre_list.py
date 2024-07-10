from http import HTTPStatus

import pytest

from functional.settings import IndexName
from functional.testdata.genre_data import (
    genre_test_data,
    genre_test_modify,
    genre_test_response_data,
    genre_test_response_modified,
)

ENDPOINT = "/api/v1/genres/"
INDEX = IndexName.GENRES.value


@pytest.mark.parametrize(
    "expected_response",
    [
        (
            {
                "body": genre_test_response_data,
                "status": HTTPStatus.OK,
            }
        )
    ],
)
@pytest.mark.asyncio
async def test_genre_get_list_elastic(
    es_load, make_get_request, expected_response
):
    """Тест выдачи списка жанров"""

    await es_load(INDEX, genre_test_data)
    response = await make_get_request(ENDPOINT)
    assert response["status"] == expected_response["status"]
    assert response["body"] == expected_response["body"]


@pytest.mark.parametrize(
    "expected_response",
    [
        (
            {
                "status": HTTPStatus.OK,
                "body_init_value": genre_test_response_data,
                "body_new_value": genre_test_response_modified,
            }
        )
    ],
)
@pytest.mark.asyncio
async def test_genre_get_list_cache(
    es_load, make_get_request, redis_client, expected_response
):
    """Тест работы кэша"""

    # индексируем в elasticsearch тестовые данные и запрашиваем их (кэшируем)
    await es_load(INDEX, genre_test_data)
    response = await make_get_request(ENDPOINT)

    # индексируем в elasticsearch скорректированные тестовые данные
    await es_load(INDEX, genre_test_modify)

    # запрашиваем тестовые данные и проверяем, что вернулись исходные тестовые данные (до корректировки)
    response = await make_get_request(ENDPOINT)
    assert response["body"] == expected_response["body_init_value"]

    # сбрасываем кэш для проверки индексации скорректированных тестовых данных
    await redis_client.flushall()
    response = await make_get_request(ENDPOINT)
    assert response["body"] == expected_response["body_new_value"]
