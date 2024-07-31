from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres.session_handler import session_handler


class DeviceModel(session_handler.base):
    __tablename__ = "device"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    user_id = Column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user_agent = Column(
        Text,
        unique=False,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    refresh_token = relationship(
        "RefreshToken",
        uselist=False,
    )
    user = relationship("User", back_populates="devices")
