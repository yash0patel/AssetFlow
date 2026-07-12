"""
app/models/booking.py
──────────────────────
Module 5 — Resource Booking

Tables:
  resource_bookings

The exclusion constraint (btree_gist) is added via Alembic migration DDL
since SQLAlchemy doesn't expose EXCLUDE USING gist natively on the ORM level.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
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
# Master: resource_bookings
# ──────────────────────────────────────────────────────────────────────────────
class ResourceBooking(Base):
    __tablename__ = "resource_bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    booked_by_employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Upcoming", server_default="Upcoming"
    )
    cancelled_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="bookings")
    booked_by_employee: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[booked_by_employee_id],
        back_populates="bookings",
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department", foreign_keys=[department_id]
    )
    cancelled_by_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[cancelled_by]
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Upcoming','Ongoing','Completed','Cancelled')",
            name="CK_resource_bookings_status",
        ),
        # end > start
        CheckConstraint(
            "end_datetime > start_datetime",
            name="CK_resource_bookings_end_after_start",
        ),
        # EXCL_resource_bookings_no_overlap is added via Alembic migration using raw DDL:
        # ALTER TABLE resource_bookings ADD CONSTRAINT EXCL_resource_bookings_no_overlap
        # EXCLUDE USING gist (asset_id WITH =, tstzrange(start_datetime, end_datetime, '[)') WITH &&)
        # WHERE (status <> 'Cancelled');
        Index("IDX_resource_bookings_asset_time", "asset_id", "start_datetime"),
        Index("IDX_resource_bookings_employee", "booked_by_employee_id", "status"),
        Index(
            "IDX_resource_bookings_status_upcoming",
            "status",
            "start_datetime",
            postgresql_where=text("status IN ('Upcoming','Ongoing')"),
        ),
        Index(
            "IDX_resource_bookings_reminder_pending",
            "start_datetime",
            postgresql_where=text("status = 'Upcoming' AND reminder_sent_at IS NULL"),
        ),
    )


# Deferred imports
from app.models.asset import Asset  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
from app.models.department import Department  # noqa: E402, F401
