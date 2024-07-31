from __future__ import annotations

import binascii
import sys
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from uuid import UUID

from argon2.exceptions import VerifyMismatchError
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import and_, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.config import get_settings
from core.exceptions import (
    DeviceNotExists,
    InvalidToken,
    InvalidUserOrPassword,
    TokenNotFoundException,
    UserNotFoundException,
)
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from db.redis.redis_storage import get_redis_storage
from models.device import DeviceModel
from models.role import Role
from models.token import RefreshToken
from models.user import User
from models.user_history import UserHistoryModel
from models.user_role import UserRoleModel
from schemas.device import DeviceCreateSchema
from schemas.token import (
    AccessTokenPayload,
    RefreshTokenInDB,
    RefreshTokenPayload,
    TokenHeader,
    UserTokenPair,
)
from schemas.user import UserBase, UserInDBAccess
from schemas.user_history import UserHistoryCreateSchema
from util.hash_helper import get_hasher
from util.JWT_helper import get_jwt_helper

if sys.version_info < (3, 9):
    from typing_extensions import Optional
else:
    from typing import Optional


class AuthService:
    def __init__(self, cache, database: PostgresStorage):
        self.cache = cache
        self.database = database
        self.refresh_token_table = RefreshToken
        self.access_table = UserRoleModel
        self.role_table = Role
        self.user_table = User
        self.device_table = DeviceModel
        self.user_history_table = UserHistoryModel
        self.token_lifetime = get_settings().acess_token_lifetime * 60

    async def login(
        self,
        session: AsyncSession,
        user: UserBase,
        user_agent: str,
        ip: str,
        oauth_provider: str = "",
    ) -> UserTokenPair:
        """Creates the new session.

        If verification successed, service returns generated tokens."""
        try:
            user_from_db = await self._get_user_with_relations_from_db(
                session=session, user_login=user.login
            )
            if not user_from_db:
                raise InvalidUserOrPassword
            current_user = UserInDBAccess.model_validate(user_from_db)
            if not oauth_provider:
                get_hasher().verify(
                    current_user.hashed_password, user.password
                )
            current_user_roles = [
                access.role.title for access in current_user.access
            ]
            device_in_db = await self._get_device_and_refresh_token_from_db(
                session=session,
                user_agent=user_agent,
                user_id=current_user.id,
            )
            if not device_in_db:
                device_obj = DeviceCreateSchema(
                    user_id=current_user.id,
                    user_agent=user_agent,
                )
                device_in_db = await self.database.create(
                    session=session,
                    obj=device_obj,
                    table=self.device_table,
                )
                device_in_db.refresh_token = None
            tokens = await self.construct_tokens(
                login=current_user.login,
                roles=current_user_roles,
                device_id=UUID(str(device_in_db.id)),
            )
            if device_in_db.refresh_token:
                device_in_db.refresh_token.refresh_token = tokens.refresh_token
                device_in_db.refresh_token.created_at = datetime.utcnow()
            else:
                device_in_db.refresh_token = RefreshToken(
                    user_id=current_user.id,
                    device_id=device_in_db.id,
                    refresh_token=tokens.refresh_token,
                )
                session.add(device_in_db.refresh_token)
            await session.commit()
        except IntegrityError:
            raise UserNotFoundException
        except VerifyMismatchError:
            raise InvalidUserOrPassword

        action = "login"
        if oauth_provider:
            action = f"login via {oauth_provider}"
        user_history_obj = UserHistoryCreateSchema(
            user_id=current_user.id,
            device_id=UUID(str(device_in_db.id)),
            action=action,
            ip=ip,
        )
        await self.write_user_history(
            session=session, user_history_obj=user_history_obj
        )
        return tokens

    async def refresh(
        self, session: AsyncSession, refresh_token: str
    ) -> UserTokenPair:
        """Generates the new token pair using the refresh token."""
        try:
            get_jwt_helper().verify_token(token=refresh_token)
            refresh_token_from_db = await self._get_refresh_token_from_db(
                session, refresh_token=refresh_token
            )
            if not refresh_token_from_db:
                raise TokenNotFoundException
            refresh_token_payload = get_jwt_helper().decode_payload(
                token=refresh_token, token_schema=RefreshTokenPayload
            )
            user_from_db = await self._get_user_with_relations_from_db(
                session=session, user_login=refresh_token_payload.sub
            )
            if not user_from_db:
                raise InvalidUserOrPassword
            current_user = UserInDBAccess.model_validate(user_from_db)
            current_user_roles = [
                access.role.title for access in current_user.access
            ]
            tokens = await self.construct_tokens(
                login=refresh_token_payload.sub,
                device_id=refresh_token_payload.device_id,
                roles=current_user_roles,
            )
            updated_token = RefreshTokenInDB(
                id=UUID(str(refresh_token_from_db.id)),
                user_id=UUID(str(refresh_token_from_db.user_id)),
                refresh_token=tokens.refresh_token,
                device_id=UUID(str(refresh_token_from_db.device_id)),
            )
            await self.database.update(
                session=session,
                obj=updated_token,
                table=self.refresh_token_table,
            )
            return tokens
        except (ValueError, binascii.Error):
            raise InvalidToken

    async def logout(
        self, session: AsyncSession, access_token: str, logout_everywhere: bool
    ) -> None:
        """Removes the current user session."""
        try:
            access_token_payload = get_jwt_helper().decode_payload(
                token=access_token, token_schema=AccessTokenPayload
            )
            user = await self._get_user_with_relations_from_db(
                session=session, user_login=access_token_payload.sub
            )
            if not user:
                raise UserNotFoundException
            if logout_everywhere:
                stmt = (delete(self.refresh_token_table)).where(
                    self.refresh_token_table.user_id == user.id
                )
                await session.execute(statement=stmt)
                await session.commit()
            else:
                device_in_db = (
                    await self._get_device_and_refresh_token_from_db_by_id(
                        session=session,
                        device_id=access_token_payload.device_id,
                    )
                )
                if not device_in_db:
                    raise DeviceNotExists
                if not device_in_db.refresh_token:
                    raise TokenNotFoundException
                await session.delete(device_in_db.refresh_token)
                await session.commit()
            await self.cache.put_to_cache(
                access_token, "deleted", self.token_lifetime
            )
        except (ValueError, binascii.Error):
            raise InvalidToken

    async def construct_tokens(
        self,
        login: str,
        device_id: UUID,
        roles: list[str],
    ) -> UserTokenPair:
        """Constucts a new token pair for a target user."""
        current_time = datetime.now(timezone.utc)

        acess_token_exp_time = current_time + timedelta(
            hours=get_settings().acess_token_lifetime
        )
        payload = AccessTokenPayload(
            sub=login,
            device_id=device_id,
            roles=roles,
            exp=str(acess_token_exp_time.timestamp()),
        )
        acess_token = get_jwt_helper().encode(TokenHeader(), payload)

        refresh_token_exp_time = current_time + timedelta(
            days=get_settings().refresh_token_lifetime
        )
        payload = RefreshTokenPayload(
            sub=login,
            device_id=device_id,
            exp=str(refresh_token_exp_time.timestamp()),
        )
        refresh_token = get_jwt_helper().encode(TokenHeader(), payload)

        return UserTokenPair(
            access_token=acess_token, refresh_token=refresh_token
        )

    async def _get_user_with_relations_from_db(
        self,
        session: AsyncSession,
        user_login: str,
    ) -> Optional[User]:
        """Helper returns the user with related objects from the database."""
        stmt = (
            select(self.user_table)
            .where(self.user_table.login == user_login)
            .options(
                joinedload(self.user_table.access).joinedload(
                    self.access_table.role
                ),
                joinedload(self.user_table.devices).joinedload(
                    self.device_table.refresh_token
                ),
                joinedload(self.user_table.oauth_accounts),
            )
        )
        result = await self.database.execute(session=session, stmt=stmt)
        return result.unique().scalars().one_or_none()

    async def _get_device_and_refresh_token_from_db(
        self,
        session: AsyncSession,
        user_id: UUID,
        user_agent: str,
    ) -> Optional[DeviceModel]:
        """Helper returns the device from the database."""
        stmt = (
            select(self.device_table)
            .where(
                and_(
                    self.device_table.user_agent == user_agent,
                    self.device_table.user_id == user_id,
                )
            )
            .options(joinedload(self.device_table.refresh_token))
        )
        result = await self.database.execute(session=session, stmt=stmt)
        return result.unique().scalars().first()

    async def _get_device_and_refresh_token_from_db_by_id(
        self,
        session: AsyncSession,
        device_id: UUID,
    ) -> Optional[DeviceModel]:
        """Helper returns the device from the database."""
        stmt = (
            select(self.device_table)
            .where(self.device_table.id == device_id)
            .options(joinedload(self.device_table.refresh_token))
        )
        result = await self.database.execute(session=session, stmt=stmt)
        return result.unique().scalars().first()

    async def _get_refresh_token_from_db(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> Optional[RefreshToken]:
        """Helper returns the token from the database."""
        stmt = select(self.refresh_token_table).where(
            self.refresh_token_table.refresh_token == refresh_token
        )
        results = await self.database.execute(session=session, stmt=stmt)
        return results.scalars().first()

    async def write_user_history(
        self, session: AsyncSession, user_history_obj: UserHistoryCreateSchema
    ):
        result = await self.database.create(
            session=session,
            obj=user_history_obj,
            table=self.user_history_table,
        )
        return result


@lru_cache(maxsize=1)
def get_auth_service(
    redis: Redis = Depends(get_redis_storage),
    postgres: PostgresStorage = Depends(get_postgers_storage),
) -> AuthService:
    return AuthService(cache=redis, database=postgres)
