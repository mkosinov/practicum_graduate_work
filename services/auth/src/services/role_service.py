from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    CommonExistsException,
    DBException,
    RoleNotFoundException,
    UpdateNoChangesException,
)
from db.postgres.postgres import PostgresStorage, get_postgers_storage
from models.role import Role
from schemas.role import (
    RoleCreateSchema,
    RoleDBSchema,
    RoleResponseSchema,
    RoleTitleSchema,
    RoleUpdateSchema,
)


class RoleService:
    def __init__(self, database: PostgresStorage):
        self.model = Role
        self.database = database

    async def list(self, session: AsyncSession) -> list[RoleResponseSchema]:
        """Get a list of the roles from the database."""
        roles = []
        roles_from_db = await self.database.get_list(
            session=session, table=self.model
        )
        if roles_from_db:
            roles = [
                RoleResponseSchema.model_validate(role_from_db)
                for role_from_db in roles_from_db
            ]
        return roles

    async def create(
        self, session: AsyncSession, role: RoleCreateSchema
    ) -> RoleDBSchema:
        """Create a role in the database."""
        try:
            role_from_db = await self.database.create(
                session=session, obj=role, table=self.model
            )
            if not role_from_db:
                raise DBException(
                    detail=f"Error while creating the role {role.title}"
                )
            return RoleDBSchema.model_validate(role_from_db)
        except IntegrityError:
            raise CommonExistsException

    async def get(
        self, session: AsyncSession, role: RoleTitleSchema
    ) -> RoleDBSchema:
        """Get a role from sthe database."""
        role_from_db = await self.database.get(
            session=session, obj=role, table=self.model
        )
        if not role_from_db:
            raise RoleNotFoundException
        return RoleDBSchema.model_validate(role_from_db)

    async def update(
        self,
        session: AsyncSession,
        role_title: RoleTitleSchema,
        update_role_data: RoleUpdateSchema,
    ) -> RoleDBSchema:
        """Patch the fields of a role in the database."""
        role_from_db = await self.database.get(
            session=session, obj=role_title, table=self.model
        )
        if not role_from_db:
            raise RoleNotFoundException
        try:
            role_update = RoleDBSchema.model_validate(role_from_db)
            if not update_role_data.title and not update_role_data.description:
                raise UpdateNoChangesException
            if update_role_data.title:
                role_update.title = update_role_data.title
            if update_role_data.description:
                role_update.description = update_role_data.description
            if (
                role_update.title == role_from_db.title
                and role_update.description == role_from_db.description
            ):
                raise UpdateNoChangesException
            role_update.modified_at = datetime.utcnow()
            updated_role_from_db = await self.database.update(
                session=session, obj=role_update, table=self.model
            )
            if not updated_role_from_db:
                raise DBException(
                    detail=f"Error while updating the role {role_title.title}"
                )
        except IntegrityError:
            raise CommonExistsException
        return RoleDBSchema.model_validate(updated_role_from_db)

    async def delete(
        self, session: AsyncSession, role: RoleTitleSchema
    ) -> None:
        """Detele a role from the database."""
        if not await self.database.delete(
            session=session, obj=role, table=self.model
        ):
            raise RoleNotFoundException


@lru_cache(maxsize=1)
def get_role_service(
    postgres: PostgresStorage = Depends(get_postgers_storage),
) -> RoleService:
    return RoleService(database=postgres)
