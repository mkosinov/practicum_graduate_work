from http import HTTPStatus

import pytest
from settings import get_settings
from testdata.access import (ASSIGN_ACCESS, CHECK_ACCESS, GET_ACCESS_LIST,
                             REMOVE_ACCESS)

pytestmark = pytest.mark.access
pytestmark = pytest.mark.asyncio

URL = f"{get_settings().api_url}/access"


@pytest.mark.parametrize("access_list", GET_ACCESS_LIST)
async def test_get_user_roles(
    access_list,
    prepare_access,
    prepare_headers_with_superuser_token,
    get_http_session,
):
    """Test getting user's roles list."""
    url = URL + "/user_roles/" + access_list["user_login"]
    response = await get_http_session.get(
        url=url, headers=prepare_headers_with_superuser_token
    )
    body = await response.json()
    status = response.status
    assert status == access_list["status"]
    if status == HTTPStatus.OK:
        assert body["user_login"] == access_list["user_login"]
        assert body["roles"] == access_list["roles"]


@pytest.mark.parametrize("access_list", CHECK_ACCESS)
async def test_get_check_user_has_role(
    access_list,
    prepare_access,
    prepare_headers_with_superuser_token,
    get_http_session,
):
    """Test verify user has a role."""
    url = (
        URL
        + f"/verify?user_login={access_list['user_login']}&role_title={access_list['role_title']}"
    )
    response = await get_http_session.get(
        url=url, headers=prepare_headers_with_superuser_token
    )
    body = await response.json()
    status = response.status
    assert status == access_list["status"]
    if status == HTTPStatus.OK:
        assert body == access_list["result"]


@pytest.mark.parametrize("access_list", ASSIGN_ACCESS)
async def test_assign_user_role(
    access_list,
    prepare_users,
    prepare_roles,
    prepare_headers_with_superuser_token,
    get_http_session,
):
    """Test assigning user a role."""
    url = URL + "/assign"
    response = await get_http_session.post(
        url=url,
        headers=prepare_headers_with_superuser_token,
        json=access_list["body"],
    )
    body = await response.json()
    status = response.status
    assert status == access_list["status"]
    if status == HTTPStatus.CREATED:
        assert body == access_list["result"]


@pytest.mark.parametrize("access_list", REMOVE_ACCESS)
async def test_remove_user_role(
    access_list,
    prepare_access,
    prepare_headers_with_superuser_token,
    get_http_session,
):
    """Test remove role from user."""
    url = URL + "/remove"
    response = await get_http_session.post(
        url=url,
        headers=prepare_headers_with_superuser_token,
        json=access_list["body"],
    )
    body = await response.json()
    status = response.status
    assert status == access_list["status"]
    if status == HTTPStatus.OK:
        assert body == access_list["result"]
