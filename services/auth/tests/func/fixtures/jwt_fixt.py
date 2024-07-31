import pytest
from Cryptodome.Hash import HMAC, SHA256
from settings import get_settings
from testdata.common import HEADERS


@pytest.fixture(scope="function")
async def get_acess_token():
    """Creates an acess token for the superuser. This acess token expires in 2027."""
    hasher = HMAC.new(
        get_settings()
        .jwt_secret.get_secret_value()
        .encode(get_settings().jwt_code),
        digestmod=SHA256,
    )
    token_without_sign = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdXBlcnVzZXIiLCJkZXZpY2VfaWQiOiI4YWZkOThjNS1hMzQ5LTQ5MDQtYjVhOC00MDNlNjE1MTc5OTkiLCJyb2xlcyI6WyJhdXRoX2FkbWluIl0sImV4cCI6IjE4MTQyMjE4NDEuOTU1MjMifQ=="
    hasher.update(token_without_sign.encode(get_settings().jwt_code))
    digest = hasher.hexdigest()

    return f"{token_without_sign}.{digest}"


@pytest.fixture(scope="function")
async def prepare_headers_with_superuser_token(get_acess_token):
    headers = HEADERS
    headers["Authorization"] = f"Bearer {get_acess_token}"

    return headers
