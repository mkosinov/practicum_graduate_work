from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres.session_handler import session_handler


class UserHistoryModel(session_handler.base):
    __tablename__ = "user_history"
    __table_args__ = (
        UniqueConstraint("id", "action"),
        {
            "postgresql_partition_by": "LIST (action)",
        },
    )

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True
    )
    user_id = Column(
        UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(
        UUID, ForeignKey("device.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(
        String(50), default="login", primary_key=True, nullable=False
    )
    ip = Column(String(39), default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="history", uselist=False)
    device = relationship("DeviceModel", uselist=False)
