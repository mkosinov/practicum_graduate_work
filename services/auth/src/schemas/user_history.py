from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserHistoryCreateSchema(BaseModel):
    user_id: UUID
    device_id: UUID
    action: str
    ip: str


class UserHistoryResponseSchema(BaseModel):
    device_user_agent: str
    action: str
    ip: str
    created_at: datetime
