from __future__ import annotations

import base64
import hashlib
import random
import secrets
import string
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.exceptions import (
    CommonExistsException,
    OauthAccountNotExistsException,
)
from core.oauth_provider import AbstractOAuthProvider
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from db.redis.redis_storage import get_redis_storage
from models.device import DeviceModel
from models.oauth import OAuthUserModel
from models.role import Role
from models.token import RefreshToken
from models.user import User
from models.user_history import UserHistoryModel
from models.user_role import UserRoleModel
from schemas.oauth import OAuthProviderDataSchema
from schemas.token import TokenCheckResponse
from schemas.user import UserBase, UserSelf
from schemas.user_history import UserHistoryCreateSchema
from services.auth_service import AuthService, get_auth_service
from services.user_service import UserService, get_user_service


class OAuthService:
    def __init__(
        self,
        cache,
        database: PostgresStorage,
        user_service: UserService,
        auth_service: AuthService,
    ):
        self.cache = cache
        self.database = database
        self.user_service = user_service
        self.auth_service = auth_service
        self.refresh_token_table = RefreshToken
        self.access_table = UserRoleModel
        self.role_table = Role
        self.user_table = User
        self.device_table = DeviceModel
        self.user_history_table = UserHistoryModel
        self.oauth_table = OAuthUserModel

    async def unlink(
        self, session: AsyncSession, provider: str, user_login: str
    ):
        """Delete oauth account."""
        stmt = (
            delete(self.oauth_table)
            .where(
                and_(
                    self.oauth_table.provider == provider,
                    self.oauth_table.user_id
                    == select(self.user_table.id)
                    .where(self.user_table.login == user_login)
                    .scalar_subquery(),
                )
            )
            .returning(self.oauth_table)
        )
        result = await session.execute(stmt)
        oauth_account = result.scalar_one_or_none()
        if not oauth_account:
            raise OauthAccountNotExistsException()
        await session.commit()
        return oauth_account

    async def link(
        self,
        session: AsyncSession,
        provider: AbstractOAuthProvider,
        code: str,
        code_verifier: str,
        ip: str,
        token_check_data: TokenCheckResponse,
    ) -> OAuthProviderDataSchema:
        """Create oauth account linked to access token user."""
        oauth_provider_data = await provider.flow(
            code=code, redirect_uri=code_verifier, code_verifier=code_verifier
        )
        stmt = (
            select(self.oauth_table, self.user_table)
            .where(
                and_(
                    self.oauth_table.provider_user_id
                    == oauth_provider_data.user_id,
                    self.oauth_table.provider == oauth_provider_data.provider,
                )
            )
            .join(self.oauth_table.user)
            .options(joinedload(self.oauth_table.user))
        )
        oauth_user = await session.scalar(stmt)
        if oauth_user:
            raise CommonExistsException(info=oauth_user)
        stmt = select(self.user_table).where(
            self.user_table.login == token_check_data.sub
        )
        result = await session.execute(stmt)
        user = result.scalar_one()
        oauth_user = OAuthUserModel(
            user_id=user.id,
            provider=oauth_provider_data.provider,
            provider_user_id=oauth_provider_data.user_id,
        )
        session.add(oauth_user)
        await session.commit()
        user_history_obj = UserHistoryCreateSchema(
            user_id=UUID(str(user.id)),
            device_id=token_check_data.device_id,
            action=f"login via {oauth_provider_data.provider}",
            ip=ip,
        )
        await self.auth_service.write_user_history(
            session=session, user_history_obj=user_history_obj
        )
        return oauth_provider_data

    async def oauth_login(
        self,
        session: AsyncSession,
        provider: AbstractOAuthProvider,
        code: str,
        code_verifier: str,
        user_agent: str,
        ip: str,
    ):
        """Login using oauth provider email"""
        oauth_provider_data = await provider.flow(
            code=code, code_verifier=code_verifier, redirect_uri=code_verifier
        )
        user = await self.get_or_create_oauth_user(
            session=session,
            oauth_provider_data=oauth_provider_data,
        )
        user_login = UserBase(login=str(user.login), password="")
        tokens = await self.auth_service.login(
            session=session,
            user=user_login,
            user_agent=user_agent,
            ip=ip,
            oauth_provider=provider.title,
        )
        return tokens

    async def get_or_create_oauth_user(
        self, session, oauth_provider_data: OAuthProviderDataSchema
    ):
        """Create oauth account and user account if not exists"""
        stmt = (
            select(self.oauth_table, self.user_table)
            .where(
                and_(
                    self.oauth_table.provider_user_id
                    == oauth_provider_data.user_id,
                    self.oauth_table.provider == oauth_provider_data.provider,
                )
            )
            .join(self.oauth_table.user)
            .options(joinedload(self.oauth_table.user))
        )
        oauth_user = await session.scalar(stmt)
        if oauth_user:
            return oauth_user.user
        stmt = select(self.user_table).where(
            self.user_table.email == oauth_provider_data.email
        )
        user = await session.scalar(stmt)
        if not user:
            new_user = UserSelf(
                login=oauth_provider_data.email,
                email=oauth_provider_data.email,
                first_name=oauth_provider_data.first_name,
                last_name=oauth_provider_data.last_name,
                password="".join(
                    [
                        secrets.choice(string.ascii_letters + string.digits)
                        for _ in range(20)
                    ]
                ),
            )
            user = await self.user_service.create_user(
                session=session, user=new_user
            )
        oauth_user = OAuthUserModel(
            user_id=user.id,
            provider=oauth_provider_data.provider,
            provider_user_id=oauth_provider_data.user_id,
        )
        session.add(oauth_user)
        await session.commit()
        return oauth_user.user

    async def create_code_challenge(
        self, state: str, code_challenge_method: str
    ):
        code_verifier = secrets.token_urlsafe(random.randint(43, 128))
        if code_challenge_method == "S256":
            hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
            encoded = base64.urlsafe_b64encode(hash)
            code_challenge = encoded.decode("ascii")[:-1]
        else:
            code_challenge = code_verifier
        await self.cache.put_to_cache(
            key=state, value=code_verifier, lifetime=600
        )
        return code_challenge


@lru_cache(maxsize=1)
def get_oauth_service(
    redis: Redis = Depends(get_redis_storage),
    postgres: PostgresStorage = Depends(get_postgers_storage),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> OAuthService:
    return OAuthService(
        cache=redis,
        database=postgres,
        user_service=user_service,
        auth_service=auth_service,
    )
