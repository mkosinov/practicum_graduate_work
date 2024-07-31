from __future__ import annotations

import sys
from http import HTTPStatus

from fastapi import APIRouter, Depends, Header, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres.session_handler import session_handler
from schemas.pagination import PaginationData
from schemas.token import TokenCheckResponse
from schemas.user import (
    UserLoginSchema,
    UserSelf,
    UserSelfResponse,
    UserSelfWRolesResponse,
)
from schemas.user_history import UserHistoryResponseSchema
from services.access_service import AccessService, get_access_service
from services.user_service import UserService, get_user_service
from util.JWT_helper import strict_token_checker

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Dict, List
else:
    from typing import Annotated, Dict, List

router = APIRouter()


@router.post(
    "/register",
    response_model=UserSelfResponse,
    status_code=HTTPStatus.CREATED,
    description="Register a new user.",
)
async def create_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    user: UserSelf,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfResponse:
    """Register a user in the authentication service."""
    new_user = await user_service.create_user(session=session, user=user)
    return UserSelfResponse(**new_user.model_dump())


@router.get(
    "/personal",
    response_model=UserSelfWRolesResponse,
    status_code=HTTPStatus.OK,
    description="Get personal user information.",
)
async def get_current_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    access_service: Annotated[AccessService, Depends(get_access_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfWRolesResponse:
    """Get data about current user."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    user = await user_service.get_user(session=session, user_login=user_login)
    user_roles = await access_service.get_user_roles(
        session=session, user_login=user_login.login
    )
    return UserSelfWRolesResponse(roles=user_roles.roles, **user.model_dump())


@router.patch(
    "/personal",
    response_model=UserSelfResponse,
    description="Change personal user information.",
)
async def update_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    update_user_data: UserSelf,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> UserSelfResponse:
    """Change personal user information."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    updated_user = await user_service.update_user(
        session=session, user=user_login, update_user_data=update_user_data
    )
    return UserSelfResponse(**updated_user.model_dump())


@router.delete("/personal", description="Delete personal data.")
async def delete_user_data(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> Dict[str, str]:
    """Delete personal information."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    await user_service.delete_user(session=session, user=user_login)
    return {"status": "User has been successfully deleted."}


@router.get(
    "/personal/history",
    response_model=List[UserHistoryResponseSchema],
    description="Get history data.",
)
async def get_current_user_history(
    user_service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    size: Annotated[int, Query(description="Page size", ge=1)] = 10,
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> List[UserHistoryResponseSchema]:
    """Get data about user browsing history."""
    user_login = UserLoginSchema(login=token_check_data.sub)
    user_history = await user_service.get_user_history(
        session=session,
        user_login=user_login,
        pagination=PaginationData(page=page - 1, size=size),
    )
    return user_history
