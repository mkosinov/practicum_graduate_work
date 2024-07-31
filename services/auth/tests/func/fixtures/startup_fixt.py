import asyncio

import asyncpg
import pytest
from aiohttp import ClientSession
from redis.asyncio import Redis
from settings import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Makes event loop."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def get_http_session():
    """Creates and closes http client."""
    client = ClientSession()
    yield client
    await client.close()


@pytest.fixture(scope="session")
async def get_redis_session():
    """Creates and closes http client."""
    redis = Redis(
        host=get_settings().auth_redis_host,
        port=get_settings().auth_redis_port,
        db=0,
        decode_responses=True,
    )
    yield redis
    await redis.aclose()


@pytest.fixture(scope="session")
async def get_postgres_session():
    """Creates and closes postgres client."""
    conn = await asyncpg.connect(
        host=get_settings().pg_host,
        port=get_settings().pg_port,
        user=get_settings().pg_user.get_secret_value(),
        password=get_settings().pg_password.get_secret_value(),
        database=get_settings().pg_db.get_secret_value(),
    )
    yield conn
    await conn.close()
