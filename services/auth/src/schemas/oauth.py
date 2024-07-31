from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OAuthUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    provider: str
    provider_user_id: int
    created_at: datetime


class OAuthProviderDataSchema(BaseModel):
    provider: str
    email: str
    user_id: int
    first_name: str
    last_name: str
