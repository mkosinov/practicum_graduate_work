from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres.session_handler import session_handler


class OAuthUserModel(session_handler.base):
    __tablename__ = "oauth_user"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(String(10), nullable=False)
    provider_user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    user = relationship("User", back_populates="oauth_accounts", uselist=False)

    UniqueConstraint(
        user_id, provider_user_id, provider, name="unique_oauth_link_to_user"
    )

    def __repr__(self) -> str:
        return f"{self.provider}"
