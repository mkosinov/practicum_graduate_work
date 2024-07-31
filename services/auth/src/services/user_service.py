from __future__ import annotations

import binascii
import random
import string
from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.exceptions import (
    CreateSuperuserException,
    DBException,
    InvalidToken,
    UserHasBeenDeletedException,
    UserNotFoundException,
)
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from models.device import DeviceModel
from models.user import User
from models.user_history import UserHistoryModel
from schemas.pagination import PaginationData
from schemas.user import (
    UserInDB,
    UserInDBOAuth,
    UserLoginSchema,
    UserSaveToDB,
    UserSelf,
)
from schemas.user_history import UserHistoryResponseSchema
from util.hash_helper import get_hasher


class UserService:
    def __init__(self, database):
        self.database = database
        self.user_table = User

    async def create_user(
        self, session: AsyncSession, user: UserSelf
    ) -> UserInDB:
        """Create user in the database."""
        if user.login == "superuser":
            raise CreateSuperuserException
        try:
            hashed_password = get_hasher().hash(user.password)
            user_db_model = UserSaveToDB(
                **user.model_dump(), hashed_password=hashed_password
            )
            new_user = await self.database.create(
                session=session, obj=user_db_model, table=self.user_table
            )
            return UserInDB.model_validate(new_user)
        except IntegrityError as e:
            raise DBException(detail=e._message())

    async def get_user(
        self, session: AsyncSession, user_login: UserLoginSchema
    ) -> UserInDBOAuth:
        """Get the user from the database."""
        try:
            user = await self.get_user_with_oauth_from_db(
                session=session, user=user_login
            )
            return user
        except (ValueError, binascii.Error):
            raise InvalidToken

    async def get_user_history(
        self,
        session: AsyncSession,
        user_login: UserLoginSchema,
        pagination: PaginationData,
    ) -> list[UserHistoryResponseSchema]:
        """Get the user history from the database."""
        try:
            user_history = await self.get_user_history_from_db(
                session=session, user=user_login, pagination=pagination
            )
            return user_history
        except (ValueError, binascii.Error):
            raise InvalidToken

    async def get_user_history_from_db(
        self,
        session: AsyncSession,
        user: UserLoginSchema,
        pagination: PaginationData,
    ) -> list[UserHistoryResponseSchema]:
        stmt = (
            select(UserHistoryModel)
            .join(User)
            .join(DeviceModel)
            .where(User.login == user.login)
            .order_by(UserHistoryModel.created_at)
            .offset(offset=pagination.size * pagination.page)
            .limit(limit=pagination.size)
            .options(joinedload(UserHistoryModel.device))
        )
        result = await self.database.execute(session=session, stmt=stmt)
        user_history_from_db = result.scalars().all()
        user_history = []
        for item in user_history_from_db:
            user_history.append(
                UserHistoryResponseSchema(
                    device_user_agent=item.device.user_agent,
                    action=item.action,
                    ip=item.ip,
                    created_at=item.created_at,
                )
            )
        return user_history

    async def get_user_from_db(
        self, session: AsyncSession, user: UserLoginSchema
    ) -> UserInDB:
        stmt = select(User).where(User.login == user.login)
        result = await self.database.execute(session=session, stmt=stmt)
        user_from_db = result.unique().scalars().first()
        if not user_from_db:
            raise UserNotFoundException
        if not user_from_db.is_active:
            raise UserHasBeenDeletedException
        return UserInDB.model_validate(user_from_db)

    async def get_user_with_oauth_from_db(
        self, session: AsyncSession, user: UserLoginSchema
    ) -> UserInDBOAuth:
        stmt = (
            select(User)
            .where(User.login == user.login)
            .options(joinedload(User.oauth_accounts))
        )
        result = await self.database.execute(session=session, stmt=stmt)
        user_from_db = result.unique().scalars().first()
        if not user_from_db:
            raise UserNotFoundException
        if not user_from_db.is_active:
            raise UserHasBeenDeletedException
        return UserInDBOAuth.model_validate(user_from_db)

    async def update_user(
        self,
        session: AsyncSession,
        user: UserLoginSchema,
        update_user_data: UserSelf,
    ) -> UserInDB:
        """Refresh user in the database."""
        try:
            updated_user_model = await self.get_user_from_db(
                session=session, user=user
            )

            if update_user_data.email:
                updated_user_model.email = update_user_data.email
            if update_user_data.login:
                updated_user_model.login = update_user_data.login
            if update_user_data.first_name:
                updated_user_model.first_name = update_user_data.first_name
            if update_user_data.last_name:
                updated_user_model.last_name = update_user_data.last_name
            if update_user_data.password:
                updated_user_model.hashed_password = get_hasher().hash(
                    update_user_data.password
                )
            updated_user_model.modified_at = datetime.utcnow()

            await self.database.update(
                session=session, obj=updated_user_model, table=self.user_table
            )
        except (ValueError, binascii.Error):
            raise InvalidToken
        except IntegrityError as e:
            raise DBException(detail=e._message())
        return updated_user_model

    async def delete_user(
        self, session: AsyncSession, user: UserLoginSchema
    ) -> None:
        """Delete user in the database. User data become invalid."""
        try:
            user_from_db = await self.get_user_from_db(
                session=session, user=user
            )
            invalid_string = get_hasher().hash(user_from_db.login)[:-20:-1]
            text = [random.choice(string.ascii_lowercase) for i in range(30)]
            update_data = UserInDB(
                id=user_from_db.id,
                login=invalid_string,
                email=("".join(text))[:-20:-1]
                + "@"
                + ("".join(text))[:-10:-1]
                + ".deleted",
                first_name=invalid_string,
                last_name=invalid_string,
                created_at=user_from_db.created_at,
                modified_at=datetime.utcnow(),
                hashed_password=user_from_db.hashed_password,
                is_active=False,
            )
            await self.database.update(
                session=session, obj=update_data, table=self.user_table
            )
        except (ValueError, binascii.Error):
            raise InvalidToken


@lru_cache(maxsize=1)
def get_user_service(
    postgres: PostgresStorage = Depends(get_postgers_storage),
) -> UserService:
    return UserService(postgres)
