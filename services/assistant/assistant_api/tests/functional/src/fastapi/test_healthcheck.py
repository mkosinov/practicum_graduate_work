from http import HTTPStatus

import httpx
from config import test_settings


def test_healthcheck() -> None:
    """Test healthcheck endpoint."""

    response = httpx.get(
        f"{test_settings.assistant_api_url}/healthcheck/liveness"
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"heathcheck": "OK"}
