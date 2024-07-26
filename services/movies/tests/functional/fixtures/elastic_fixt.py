from typing import AsyncGenerator

import pytest
from elasticsearch import AsyncElasticsearch, helpers

from functional.settings import IndexName, index_settings, test_settings


@pytest.fixture(scope="session")
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    """Создаем клиента для работы с Elasticsearch. В конце закрываем его."""

    client = AsyncElasticsearch(hosts=[test_settings.es_url])
    yield client
    await client.close()


@pytest.fixture(autouse=True)
async def create_indexes(es_client: AsyncElasticsearch):
    """Создаем индексы для Elasticsearch, предварительно удалив старые"""

    for index_name in IndexName:
        index_name = index_name.value
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(
            index=index_name,
            mappings=index_settings.MAPPINGS[index_name],
            settings=index_settings.SETTINGS,
        )


@pytest.fixture
def es_load(es_client: AsyncElasticsearch):
    """Загружаем данные в индекс."""

    async def inner(index_name: str, data: list[dict]):
        actions = [
            {
                "_index": index_name,
                "_id": row["uuid"],
                "_source": row,
            }
            for row in data
        ]
        await helpers.async_bulk(es_client, actions, refresh=True)

    return inner
