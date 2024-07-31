from __future__ import annotations

from pydantic import BaseModel, Field


class PaginationData(BaseModel):
    page: int = Field(ge=0)
    size: int = Field(ge=1)
