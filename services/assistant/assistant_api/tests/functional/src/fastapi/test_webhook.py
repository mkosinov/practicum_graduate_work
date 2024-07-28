import json
from http import HTTPStatus

import httpx
import pytest
from config import test_settings

from src.test_data.alice import data


@pytest.mark.parametrize("request_, expected_response", data)
def test_webhook(request_, expected_response) -> None:
    """Test webhook endpoint."""

    response = httpx.post(
        url=f"{test_settings.assistant_api_url}/webhook/alice",
        headers={"Content-Type": "application/json"},
        json=json.loads(request_),
    )

    assert response.status_code == HTTPStatus.OK
    assert str(response.json()) == expected_response
