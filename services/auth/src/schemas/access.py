from __future__ import annotations

import sys
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from core.config import get_settings

if sys.version_info < (3, 9):
    from typing_extensions import List
else:
    from typing import List


class AccessInSchema(BaseModel):
    """Schema for an input data with validation."""

    user_login: str = Field(
        pattern=get_settings().login_pattern,
        description=f"User login. Letters and digits only. {get_settings().login_min_length}-{get_settings().login_max_length} characters long.",
    )
    role_title: str = Field(
        pattern=get_settings().role_title_pattern,
        description=f"Role title. Letters and digits only. {get_settings().role_title_min_length}-{get_settings().role_title_max_length} characters long.",
    )


class AccessDBSchema(BaseModel):
    """Schema for DB operations."""

    model_config = ConfigDict(from_attributes=True, extra="allow")

    user_id: UUID
    role_id: UUID


class ShowUserAccessSchema(BaseModel):
    """Schema with roles list for user."""

    user_login: str
    roles: List[str] = []
