from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from core.exceptions import (
    AccessNotFoundException,
    CommonExistsException,
    DBException,
    RoleNotFoundException,
    UserNotFoundException,
)
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from models.role import Role
from models.user import User
from models.user_role import UserRoleModel
from schemas.access import AccessDBSchema, AccessInSchema, ShowUserAccessSchema
from schemas.role import RoleTitleSchema
from schemas.user import UserLoginSchema


class AccessService:
    def __init__(self, database):
        self.model = UserRoleModel
        self.user_table = User
        self.role_table = Role
        self.database = database

    async def create(
        self, session: AsyncSession, access: AccessInSchema
    ) -> AccessDBSchema:
        """Create a user_role in the database."""
        access_to_db = await self._access_lookup_ids(
            session=session, access=access
        )
        try:
            access_from_db = await self.database.create(
                session=session, obj=access_to_db, table=self.model
            )

            if not access_from_db:
                raise DBException(
                    detail=f"Error while creating the access {access.user_login}:{access.role_title}"
                )
            return AccessDBSchema.model_validate(access_from_db)
        except IntegrityError:
            raise CommonExistsException

    async def delete(
        self, session: AsyncSession, access: AccessInSchema
    ) -> AccessDBSchema:
        """Detele a user_role from the database."""
        access_to_db = await self._access_lookup_ids(
            session=session, access=access
        )
        access_from_db = await self.database.delete(
            session=session, obj=access_to_db, table=self.model
        )
        if not access_from_db:
            raise AccessNotFoundException
        return AccessDBSchema.model_validate(access_from_db)

    async def get(self, session: AsyncSession, access: AccessInSchema) -> bool:
        """Get a user_role from the database."""
        access_to_db = await self._access_lookup_ids(
            session=session, access=access
        )
        if not await self.database.get(
            session=session, obj=access_to_db, table=self.model
        ):
            return False
        return True

    async def get_user_roles(
        self, session: AsyncSession, user_login: str
    ) -> ShowUserAccessSchema:
        """Get all user_roles using user_login."""
        stmt = (
            select(self.user_table)
            .where(self.user_table.login == user_login)
            .options(
                joinedload(self.user_table.access).joinedload(self.model.role)
            )
        )
        result = await self.database.execute(session=session, stmt=stmt)
        user_from_db = result.unique().scalars().one_or_none()
        if not user_from_db:
            raise UserNotFoundException
        access = ShowUserAccessSchema(user_login=user_login)
        access.roles = [
            user_access.role.title for user_access in user_from_db.access
        ]
        return access

    async def _access_lookup_ids(
        self, session: AsyncSession, access: AccessInSchema
    ):
        user_login = UserLoginSchema(login=access.user_login)
        role_title = RoleTitleSchema(title=access.role_title)
        user = await self.database.get(
            session=session, obj=user_login, table=self.user_table
        )
        if not user:
            raise UserNotFoundException
        role = await self.database.get(
            session=session, obj=role_title, table=self.role_table
        )
        if not role:
            raise RoleNotFoundException
        return AccessDBSchema(user_id=user.id, role_id=role.id)


@lru_cache(maxsize=1)
def get_access_service(
    postgres: PostgresStorage = Depends(get_postgers_storage),
):
    return AccessService(database=postgres)
