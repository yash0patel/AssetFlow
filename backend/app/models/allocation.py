"""
app/models/allocation.py
─────────────────────────
Module 4 — Asset Allocation

Tables:
  asset_allocations
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
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
# Master: asset_allocations
# ──────────────────────────────────────────────────────────────────────────────
class AssetAllocation(Base):
    __tablename__ = "asset_allocations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    allocated_to_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=True
    )
    allocated_to_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=True
    )
    allocated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    allocation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    expected_return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_return_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    return_condition: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    return_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    returned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Active", server_default="Active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="allocations")
    allocated_to_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        foreign_keys=[allocated_to_employee_id],
        back_populates="allocations",
    )
    allocated_to_department: Mapped[Optional["Department"]] = relationship(
        "Department", foreign_keys=[allocated_to_department_id]
    )
    allocator: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[allocated_by]
    )
    returner: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[returned_by]
    )
    transfer_requests: Mapped[list["AssetTransferRequest"]] = relationship(
        "AssetTransferRequest",
        foreign_keys="AssetTransferRequest.current_allocation_id",
        back_populates="current_allocation",
    )

    __table_args__ = (
        CheckConstraint(
            "return_condition IN ('New','Good','Fair','Poor','Damaged')",
            name="CK_asset_allocations_return_condition",
        ),
        CheckConstraint(
            "status IN ('Active','Returned','Overdue','Lost')",
            name="CK_asset_allocations_status",
        ),
        # THE double-allocation block — at most one Active row per asset
        Index(
            "UK_asset_allocations_one_active",
            "asset_id",
            unique=True,
            postgresql_where=text("status = 'Active'"),
        ),
        # Exactly one of employee/department must be set — enforced via DB check
        CheckConstraint(
            "(allocated_to_employee_id IS NOT NULL) <> (allocated_to_department_id IS NOT NULL)",
            name="CK_asset_allocations_one_target",
        ),
        Index("IDX_asset_allocations_asset_history", "asset_id", "allocation_date"),
        Index("IDX_asset_allocations_employee", "allocated_to_employee_id", "status"),
        Index("IDX_asset_allocations_department", "allocated_to_department_id", "status"),
        Index(
            "IDX_asset_allocations_overdue",
            "expected_return_date",
            postgresql_where=text("status = 'Active'"),
        ),
    )


# Deferred imports
from app.models.asset import Asset  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
from app.models.department import Department  # noqa: E402, F401
from app.models.transfer import AssetTransferRequest  # noqa: E402, F401
