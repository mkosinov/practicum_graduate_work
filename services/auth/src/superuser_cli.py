from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

import typer
from rich import print
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from db.postgres.session_handler import session_handler
from models.device import DeviceModel  # noqa
from models.oauth import OAuthUserModel  # noqa
from models.token import RefreshToken  # noqa
from models.user import User  # noqa
from models.user_history import UserHistoryModel  # noqa
from models.user_role import UserRoleModel  # noqa
from util.hash_helper import get_hasher  # noqa

typer_app = typer.Typer()


@typer_app.command()
def create_supersuser(password: str):
    """Specify superuser`s password. Account with login 'superuser' will be created or updated with password provided"""
    hashed_password = get_hasher().hash(password)
    superuser = User(
        id=uuid.uuid4(),
        login="superuser",
        email="superuser@superuser.com",
        hashed_password=hashed_password,
        first_name="superuser",
        last_name="superuser",
        created_at=datetime.now(),
        modified_at=datetime.now(),
        is_active=True,
    )
    asyncio.run(create_or_update_superuser(superuser))


async def create_or_update_superuser(superuser):
    session_generator = session_handler.create_session()
    db_session = await anext(session_generator)
    try:
        if await _insert_data_in_db(db_session=db_session, obj=superuser):
            print("[bold green]Superuser created[/bold green]")
            return True
        if await _update_data_in_db(db_session=db_session, obj=superuser):
            print("[bold green]Superuser password updated[/bold green]")
            return True
        print("[bold red]Can't update existing password[/bold red]")
        raise typer.Exit(code=1)
    finally:
        await db_session.close()


async def _insert_data_in_db(db_session, obj):
    """Inserts object to db table"""
    try:
        db_session.add(obj)
        await db_session.commit()
        return obj
    except IntegrityError as e:
        print(
            f"[bold red]Can't create new superuser, because some values are occupied[/bold red]: {str(e.orig).split('DETAIL: ')[1]}\n[bold yellow]Try to update password in existing superuser account[/bold yellow]",
        )
        await db_session.rollback()
        return None


async def _update_data_in_db(db_session, obj):
    """Update object to db table"""
    results = await db_session.scalars(select(User).filter_by(login=obj.login))
    obj_from_db = results.first()
    obj_from_db.hashed_password = obj.hashed_password
    await db_session.commit()
    return obj_from_db


if __name__ == "__main__":
    typer_app()
