"""
app/models/notification.py
───────────────────────────
Module 8 — Notifications

Tables:
  notifications, notification_preferences

Both tables are range-partitioned by created_at in production (monthly).
Modeled here as regular tables; partitioning is managed via Alembic raw DDL.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# High-volume: notifications (range-partitioned by created_at)
# ──────────────────────────────────────────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
    category: Mapped[str] = mapped_column(String(15), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    recipient_user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        CheckConstraint(
            "notification_type IN ("
            "'AssetAssigned','MaintenanceApproved','MaintenanceRejected',"
            "'BookingConfirmed','BookingCancelled','BookingReminder',"
            "'TransferApproved','OverdueReturn','AuditDiscrepancy')",
            name="CK_notifications_type",
        ),
        CheckConstraint(
            "category IN ('Alert','Approval','Booking')", name="CK_notifications_category"
        ),
        # Bell icon unread list — single most frequent query in the module
        Index(
            "IDX_notifications_recipient_unread",
            "recipient_user_id",
            "is_read",
            "created_at",
        ),
        # Screen 10 tab filters
        Index(
            "IDX_notifications_category",
            "recipient_user_id",
            "category",
            "created_at",
        ),
        Index("IDX_notifications_reference", "reference_type", "reference_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Master: notification_preferences
# ──────────────────────────────────────────────────────────────────────────────
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    notification_type: Mapped[str] = mapped_column(String(40), primary_key=True)
    channel: Mapped[str] = mapped_column(String(15), primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        CheckConstraint(
            "channel IN ('InApp','Email')", name="CK_notification_preferences_channel"
        ),
        Index("IDX_notification_preferences_user", "user_id"),
    )


# Deferred imports
from app.models.user import User  # noqa: E402, F401
