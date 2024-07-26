import json
from http import HTTPStatus

import httpx
import pytest
from pymongo import MongoClient

from functional.config import test_settings
from src.test_data.alice import data

mongo_client = MongoClient("mongodb://localhost:27017")


@pytest.mark.parametrize("request, expected_response", data)
def test_webhook(request, expected_response) -> None:
    """Test webhook endpoint."""

    response = httpx.post(
        f"{test_settings.service_url}/api/v1/webhook/alice",
        json=request,
        headers={"Content-Type": "application/json"},
    )
    assert response.status == HTTPStatus.OK
    assert response.json() == json.loads(expected_response)
