"""
app/models/maintenance.py
──────────────────────────
Module 6 — Maintenance Management

Tables:
  maintenance_technicians, maintenance_requests, maintenance_status_history
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
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Master/Lookup: maintenance_technicians
# ──────────────────────────────────────────────────────────────────────────────
class MaintenanceTechnician(Base):
    __tablename__ = "maintenance_technicians"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_external_vendor: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    contact_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    # Relationships
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="technician"
    )

    __table_args__ = (
        Index("IDX_maintenance_technicians_specialization", "specialization"),
        Index("IDX_maintenance_technicians_active", "is_active"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Master: maintenance_requests
# ──────────────────────────────────────────────────────────────────────────────
class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    request_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    raised_by_employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(10), nullable=False, default="Medium", server_default="Medium"
    )
    status: Mapped[str] = mapped_column(
        String(25), nullable=False, default="Pending", server_default="Pending"
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technician_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("maintenance_technicians.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 2), nullable=True)
    actual_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_requests")
    raised_by_employee: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[raised_by_employee_id],
        back_populates="maintenance_requests_raised",
    )
    approver: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[approved_by]
    )
    technician: Mapped[Optional["MaintenanceTechnician"]] = relationship(
        "MaintenanceTechnician", back_populates="maintenance_requests"
    )
    status_history: Mapped[list["MaintenanceStatusHistory"]] = relationship(
        "MaintenanceStatusHistory", back_populates="maintenance_request"
    )

    __table_args__ = (
        CheckConstraint(
            "priority IN ('Low','Medium','High','Critical')",
            name="CK_maintenance_requests_priority",
        ),
        CheckConstraint(
            "status IN ('Pending','Approved','Rejected','Technician Assigned','In Progress','Resolved')",
            name="CK_maintenance_requests_status",
        ),
        # Kanban board rendering: column + priority + age
        Index("IDX_maintenance_kanban", "status", "priority", "created_at"),
        Index("IDX_maintenance_asset", "asset_id", "created_at"),
        Index("IDX_maintenance_technician", "technician_id", "status"),
        Index(
            "IDX_maintenance_pending",
            "status",
            postgresql_where=text("status = 'Pending'"),
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# History: maintenance_status_history
# ──────────────────────────────────────────────────────────────────────────────
class MaintenanceStatusHistory(Base):
    __tablename__ = "maintenance_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    maintenance_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("maintenance_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    previous_status: Mapped[Optional[str]] = mapped_column(String(25), nullable=True)
    new_status: Mapped[str] = mapped_column(String(25), nullable=False)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    maintenance_request: Mapped["MaintenanceRequest"] = relationship(
        "MaintenanceRequest", back_populates="status_history"
    )
    changed_by_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[changed_by]
    )

    __table_args__ = (
        Index("IDX_maintenance_status_history_request", "maintenance_request_id", "changed_at"),
    )


# Deferred imports
from app.models.asset import Asset  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
