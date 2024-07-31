from __future__ import annotations

import sys
import uuid
from http import HTTPStatus

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Security,
)
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.oauth_provider import CodeChallengeMethod, OAuthProviders
from db.postgres.session_handler import session_handler
from db.redis.redis_storage import RedisStorage, get_redis_storage
from schemas.oauth import OAuthProviderDataSchema
from schemas.token import TokenCheckResponse, UserTokenPair
from services.oauth_service import OAuthService, get_oauth_service
from util.JWT_helper import silent_token_checker, strict_token_checker

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Optional, Union
else:
    from typing import Annotated, Optional, Union

router = APIRouter()


@router.get("/unlink/{provider}")
async def unlink_oauth_account(
    provider: Annotated[str, Path()],
    token_check_data: Annotated[
        TokenCheckResponse, Security(strict_token_checker)
    ],
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
):
    oauth_account = await oauth_service.unlink(
        session=session, provider=provider, user_login=token_check_data.sub
    )
    return {
        "status": f"{oauth_account.provider} account has been successfully detached."
    }


@router.get(
    "/page/{provider}",
    description="URL to redirect users to Authorization provider page.",
)
async def oauth_redirect_page(
    provider: Annotated[str, Path()],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    state: Annotated[Optional[str], Query()] = None,
):
    if provider not in OAuthProviders._member_names_:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Not supported auth provider",
        )
    code_url_path = router.url_path_for("oauth_code", provider=provider)
    redirect_uri = get_settings().oauth_base_url + str(code_url_path)
    if not state:
        state = str(uuid.uuid4())
    if provider == OAuthProviders.yandex.name:
        code_challenge = await oauth_service.create_code_challenge(
            state=state, code_challenge_method=CodeChallengeMethod.S256.value
        )
        oauth_provider_url = (
            OAuthProviders.yandex.value.oauth_provider_authorization_page_url(
                redirect_uri=redirect_uri,
                state=state,
                code_challenge=code_challenge,
            )
        )
    if provider == OAuthProviders.vk.name:
        oauth_provider_url = (
            OAuthProviders.vk.value.oauth_provider_authorization_page_url(
                redirect_uri=redirect_uri
            )
        )
    return RedirectResponse(oauth_provider_url, status_code=307)


@router.get(
    "/code/{provider}",
    status_code=HTTPStatus.OK,
    description="URL to get authorization code from Authorization provider and login/register user.",
)
async def oauth_code(
    request: Request,
    session: Annotated[AsyncSession, Depends(session_handler.create_session)],
    cache_service: Annotated[RedisStorage, Depends(get_redis_storage)],
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    provider: Annotated[str, Path()],
    token_check_data: Annotated[
        Optional[TokenCheckResponse], Security(silent_token_checker)
    ] = None,
    user_agent: Annotated[str, Header()] = "",
    real_ip: Annotated[str, Header(alias="X-Real-IP")] = "",
    code: Annotated[Optional[str], Query()] = None,
    error: Annotated[Optional[str], Query()] = None,
    error_description: Annotated[Optional[str], Query()] = None,
    state: Annotated[Optional[str], Query()] = None,
) -> Union[UserTokenPair, OAuthProviderDataSchema]:
    if provider not in OAuthProviders._member_names_:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Not supported auth provider",
        )
    if error:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=error_description
        )
    if not code:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="No authorization code provided",
        )
    if state:
        code_verifier = await cache_service.get_from_cache(key=state)
    else:
        code_verifier = str(request.url).split("?")[0]
    if token_check_data:
        result = await oauth_service.link(
            session=session,
            provider=OAuthProviders[f"{provider}"].value,
            code=code,
            code_verifier=code_verifier,
            ip=real_ip,
            token_check_data=token_check_data,
        )
    else:
        result = await oauth_service.oauth_login(
            session=session,
            provider=OAuthProviders[f"{provider}"].value,
            code=code,
            code_verifier=code_verifier,
            user_agent=user_agent,
            ip=real_ip,
        )
    return result
