import asyncio
from typing import Any, AsyncGenerator, Callable, Coroutine

import pytest
from aiohttp import ClientSession

from functional.settings import test_settings


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop."""

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def a_client() -> AsyncGenerator[ClientSession, None]:
    """Получаем клиента, с помощью которого будем делать запросы.
    В конце закрываем его.
    """

    client = ClientSession()
    yield client
    await client.close()


@pytest.fixture
def make_get_request(
    a_client: ClientSession,
) -> Callable[[str, dict | None], Coroutine[Any, Any, dict[str, Any]]]:
    """Делаем GET запрос на определенный endpoint, передавая параметры.
    Получаем ответ.
    """

    async def inner(
        endpoint: str, params: dict | None = None
    ) -> dict[str, Any]:
        params = params or {}
        url = f"{test_settings.app_url}{endpoint}"
        async with a_client.get(url=url, params=params) as resp:
            return {
                "body": await resp.json(),
                "status": resp.status,
                "headers": resp.headers,
                "url": resp.url,
            }

    return inner
