"""
app/models/activity_log.py
───────────────────────────
Module 8 — Activity Logs

Tables:
  activity_logs

Append-only audit trail. Range-partitioned by created_at (monthly).
Modeled as regular table; partitioning via Alembic raw DDL.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Append-only: activity_logs
# ──────────────────────────────────────────────────────────────────────────────
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized snapshot of actor's role at the time (roles can change later)
    actor_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    actor_user: Mapped[Optional["User"]] = relationship("User", back_populates="activity_logs")

    __table_args__ = (
        CheckConstraint(
            "action IN ('Create','Update','Delete','Approve','Reject','Cancel','Close','Login','Logout')",
            name="CK_activity_logs_action",
        ),
        # "What did user X do"
        Index("IDX_activity_logs_actor", "actor_user_id", "created_at"),
        # "Full history of this specific record"
        Index("IDX_activity_logs_entity", "entity_type", "entity_id", "created_at"),
        # Module-level audit reports
        Index("IDX_activity_logs_module", "module_name", "created_at"),
    )


# Deferred imports
from app.models.user import User  # noqa: E402, F401
