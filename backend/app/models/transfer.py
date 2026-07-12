"""
app/models/transfer.py
───────────────────────
Module 4 — Asset Transfer Requests

Tables:
  asset_transfer_requests
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
# Master: asset_transfer_requests
# ──────────────────────────────────────────────────────────────────────────────
class AssetTransferRequest(Base):
    __tablename__ = "asset_transfer_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    current_allocation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_allocations.id", ondelete="RESTRICT"), nullable=False
    )
    # Denormalized snapshot of current holder at request time
    from_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    to_employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Requested", server_default="Requested"
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="transfer_requests")
    current_allocation: Mapped["AssetAllocation"] = relationship(
        "AssetAllocation",
        foreign_keys=[current_allocation_id],
        back_populates="transfer_requests",
    )
    from_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[from_employee_id]
    )
    to_employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[to_employee_id])
    requester: Mapped["Employee"] = relationship("Employee", foreign_keys=[requested_by])
    approver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[approved_by])

    __table_args__ = (
        CheckConstraint(
            "status IN ('Requested','Approved','Rejected','Completed','Cancelled')",
            name="CK_asset_transfer_requests_status",
        ),
        Index("IDX_transfer_requests_asset", "asset_id", "status"),
        Index(
            "IDX_transfer_requests_pending",
            "status",
            postgresql_where=text("status = 'Requested'"),
        ),
        Index("IDX_transfer_requests_to_employee", "to_employee_id"),
    )


# Deferred imports
from app.models.asset import Asset  # noqa: E402, F401
from app.models.allocation import AssetAllocation  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
