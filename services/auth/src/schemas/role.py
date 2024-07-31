from __future__ import annotations

import sys
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.config import get_settings
from schemas.mixins import CreatedMixinSchema

if sys.version_info < (3, 9):
    from typing_extensions import Optional
else:
    from typing import Optional


class RoleTitleSchema(BaseModel):
    title: str


class RoleCreateSchema(BaseModel):
    title: str = Field(
        pattern=get_settings().role_title_pattern,
        description="Role title. Letters and digits only. 3-50 characters long.",
    )

    description: str = Field(
        default="", max_length=get_settings().role_description_max_length
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "auth_admin",
                    "description": "Manager for roles and gives roles to other users",
                }
            ]
        }
    }


class RoleUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "auth_admin",
                    "description": "Manager for roles and gives roles to other users",
                }
            ]
        }
    }

    @field_validator("title")
    @classmethod
    def title_validator(cls, title: str) -> str:
        if isinstance(title, str):
            RoleCreateSchema(title=title)
            return title
        raise ValueError


class RoleResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str


class RoleDBSchema(CreatedMixinSchema, RoleResponseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
