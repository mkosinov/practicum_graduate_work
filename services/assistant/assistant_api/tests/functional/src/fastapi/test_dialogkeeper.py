from http import HTTPStatus

import httpx
from config import test_settings
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017")


async def test_dialogkeeper() -> None:
    """Test dialogkeeper endpoint."""

    response = httpx.get(
        url=f"{test_settings.assistant_api_url}/dialogkeeper",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()
