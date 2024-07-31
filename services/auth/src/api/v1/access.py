from __future__ import annotations

import sys
from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, Header, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.postgres.session_handler import session_handler
from schemas.access import AccessDBSchema, AccessInSchema, ShowUserAccessSchema
from services.access_service import AccessService, get_access_service

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Any
else:
    from typing import Annotated, Any

router = APIRouter()


@router.post(
    "/assign",
    response_model=AccessDBSchema,
    description="Assign a role to the user",
    status_code=HTTPStatus.CREATED,
)
async def assign_user_role(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    access_service: Annotated[Any, Depends(get_access_service)],
    access: AccessInSchema = Body(
        description="Specify a user login and a role title to give role to the user"
    ),
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> AccessDBSchema:
    """Assign a role to the user"""
    result = await access_service.create(session=session, access=access)
    return result


@router.post(
    "/remove",
    response_model=AccessDBSchema,
    description="Remove role from user",
    status_code=HTTPStatus.OK,
)
async def remove_user_role(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    access_service: Annotated[AccessService, Depends(get_access_service)],
    access: AccessInSchema = Body(
        description="Specify user login and role title to remove role to user"
    ),
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> AccessDBSchema:
    """Remove role to user"""
    result = await access_service.delete(session=session, access=access)
    return result


@router.get(
    "/verify",
    response_model=None,
    description="Verify user has role",
    status_code=HTTPStatus.OK,
)
async def verify_user_has_role(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    access_service: Annotated[AccessService, Depends(get_access_service)],
    user_login: Annotated[str, Query(pattern=get_settings().login_pattern)],
    role_title: Annotated[
        str, Query(pattern=get_settings().role_title_pattern)
    ],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> bool:
    """Verify user has role"""
    access = AccessInSchema(user_login=user_login, role_title=role_title)
    result = await access_service.get(session=session, access=access)
    return result


@router.get(
    "/user_roles/{user_login}",
    response_model=ShowUserAccessSchema,
    description="Get role information",
    status_code=HTTPStatus.OK,
)
async def list_user_roles(
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    access_service: Annotated[AccessService, Depends(get_access_service)],
    user_login: Annotated[str, Path(pattern=get_settings().login_pattern)],
    request_id: Annotated[str, Header(alias="X-Request-Id")] = "",
) -> ShowUserAccessSchema:
    """Get all user roles"""
    result = await access_service.get_user_roles(
        session=session, user_login=user_login
    )
    return result
