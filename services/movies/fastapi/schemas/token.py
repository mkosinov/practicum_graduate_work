from uuid import UUID

from pydantic import BaseModel


class AccessTokenPayload(BaseModel):
    sub: str
    device_id: UUID
    roles: list[str]
    exp: str
