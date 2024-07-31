from __future__ import annotations

import sys
from uuid import UUID

from pydantic import BaseModel, Field

if sys.version_info < (3, 9):
    from typing_extensions import List
else:
    from typing import List


class UserTokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class TokenHeader(BaseModel):
    typ: str = Field(default="JWT")
    alg: str = Field(default="HS256")


class AccessTokenPayload(BaseModel):
    sub: str
    device_id: UUID
    roles: List[str]
    exp: str


class RefreshTokenPayload(BaseModel):
    sub: str
    device_id: UUID
    exp: str


class RefreshTokenInDB(BaseModel):
    id: UUID
    user_id: UUID
    device_id: UUID
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenCheckResponse(AccessTokenPayload):
    token: str
