from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class DeviceCreateSchema(BaseModel):
    user_id: UUID
    user_agent: str
