from __future__ import annotations

import sys
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from core.config import get_settings
from schemas.mixins import CreatedMixinSchema
from schemas.oauth import OAuthUserSchema

if sys.version_info < (3, 9):
    from typing_extensions import List
else:
    from typing import List


class UserSelf(BaseModel):
    login: str = Field(
        min_length=get_settings().login_min_length,
        max_length=get_settings().login_max_length,
    )
    email: EmailStr = Field(
        min_length=get_settings().email_min_length,
        max_length=get_settings().email_max_length,
    )
    first_name: str = Field(
        min_length=get_settings().first_name_min_length,
        max_length=get_settings().first_name_max_length,
    )
    last_name: str = Field(
        min_length=get_settings().last_name_min_length,
        max_length=get_settings().last_name_max_length,
    )
    password: str = Field(
        min_length=get_settings().password_min_length,
        max_length=get_settings().password_max_length,
    )


class UserInDB(CreatedMixinSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    hashed_password: str


class UserInDBOAuth(UserInDB):
    oauth_accounts: List[OAuthUserSchema] = []


class UserInDBAccess(UserInDB):
    model_config = ConfigDict(from_attributes=True)
    access: List = []


class UserSaveToDB(BaseModel):
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    hashed_password: str


class UserBase(BaseModel):
    login: str
    password: str


class UserLogin(BaseModel):
    login: str
    acess_token: str


class UserSelfResponse(BaseModel):
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    oauth_accounts: List[OAuthUserSchema] = Field(exclude=True, default=[])

    @computed_field
    @property
    def oauth_accounts_compact(self) -> List[str]:
        return [account.provider for account in self.oauth_accounts]


class UserSelfWRolesResponse(UserSelfResponse):
    roles: List[str]


class UserLoginSchema(BaseModel):
    login: str
