"""
app/models/audit.py
────────────────────
Module 7 — Asset Audit

Tables:
  audit_cycles, audit_cycle_auditors, audit_cycle_items, audit_discrepancy_reports
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Master: audit_cycles
# ──────────────────────────────────────────────────────────────────────────────
class AuditCycle(Base):
    __tablename__ = "audit_cycles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    cycle_name: Mapped[str] = mapped_column(String(150), nullable=False)
    scope_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    scope_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_locations.id", ondelete="SET NULL"), nullable=True
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Planned", server_default="Planned"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    closed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    scope_department: Mapped[Optional["Department"]] = relationship(
        "Department", foreign_keys=[scope_department_id]
    )
    scope_location: Mapped[Optional["AssetLocation"]] = relationship(
        "AssetLocation", foreign_keys=[scope_location_id]
    )
    creator: Mapped["Employee"] = relationship("Employee", foreign_keys=[created_by])
    closer: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[closed_by])
    auditors: Mapped[list["AuditCycleAuditor"]] = relationship(
        "AuditCycleAuditor", back_populates="audit_cycle"
    )
    items: Mapped[list["AuditCycleItem"]] = relationship(
        "AuditCycleItem", back_populates="audit_cycle"
    )
    discrepancy_reports: Mapped[list["AuditDiscrepancyReport"]] = relationship(
        "AuditDiscrepancyReport", back_populates="audit_cycle"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Planned','In Progress','Closed')", name="CK_audit_cycles_status"
        ),
        CheckConstraint("end_date >= start_date", name="CK_audit_cycles_dates"),
        Index("IDX_audit_cycles_status", "status"),
        Index("IDX_audit_cycles_department", "scope_department_id"),
        Index("IDX_audit_cycles_dates", "start_date", "end_date"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Junction: audit_cycle_auditors
# ──────────────────────────────────────────────────────────────────────────────
class AuditCycleAuditor(Base):
    __tablename__ = "audit_cycle_auditors"

    audit_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_cycles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    audit_cycle: Mapped["AuditCycle"] = relationship("AuditCycle", back_populates="auditors")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="audit_assignments")

    __table_args__ = (Index("IDX_audit_auditors_employee", "employee_id"),)


# ──────────────────────────────────────────────────────────────────────────────
# Transactional: audit_cycle_items (high-volume checklist)
# ──────────────────────────────────────────────────────────────────────────────
class AuditCycleItem(Base):
    __tablename__ = "audit_cycle_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    audit_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    expected_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_locations.id", ondelete="SET NULL"), nullable=True
    )
    verification_status: Mapped[str] = mapped_column(
        String(15), nullable=False, default="Pending", server_default="Pending"
    )
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    audit_cycle: Mapped["AuditCycle"] = relationship("AuditCycle", back_populates="items")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="audit_items")
    expected_location: Mapped[Optional["AssetLocation"]] = relationship(
        "AssetLocation", foreign_keys=[expected_location_id]
    )
    verifier: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[verified_by])
    discrepancy_report: Mapped[Optional["AuditDiscrepancyReport"]] = relationship(
        "AuditDiscrepancyReport",
        foreign_keys="AuditDiscrepancyReport.audit_cycle_item_id",
        back_populates="audit_cycle_item",
        uselist=False,
    )

    __table_args__ = (
        CheckConstraint(
            "verification_status IN ('Pending','Verified','Missing','Damaged')",
            name="CK_audit_cycle_items_status",
        ),
        UniqueConstraint("audit_cycle_id", "asset_id", name="UK_audit_cycle_items"),
        Index("IDX_audit_items_cycle_status", "audit_cycle_id", "verification_status"),
        Index("IDX_audit_items_asset", "asset_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Derived: audit_discrepancy_reports
# ──────────────────────────────────────────────────────────────────────────────
class AuditDiscrepancyReport(Base):
    __tablename__ = "audit_discrepancy_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    audit_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False
    )
    audit_cycle_item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("audit_cycle_items.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False
    )
    discrepancy_type: Mapped[str] = mapped_column(String(15), nullable=False)
    auto_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    resolution_status: Mapped[str] = mapped_column(
        String(15), nullable=False, default="Open", server_default="Open"
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    audit_cycle: Mapped["AuditCycle"] = relationship(
        "AuditCycle", back_populates="discrepancy_reports"
    )
    audit_cycle_item: Mapped["AuditCycleItem"] = relationship(
        "AuditCycleItem", back_populates="discrepancy_report", foreign_keys=[audit_cycle_item_id]
    )
    asset: Mapped["Asset"] = relationship("Asset", foreign_keys=[asset_id])
    resolver: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[resolved_by])

    __table_args__ = (
        CheckConstraint(
            "discrepancy_type IN ('Missing','Damaged')",
            name="CK_audit_discrepancy_reports_type",
        ),
        CheckConstraint(
            "resolution_status IN ('Open','Resolved')",
            name="CK_audit_discrepancy_reports_resolution",
        ),
        Index("IDX_discrepancy_cycle", "audit_cycle_id"),
        Index(
            "IDX_discrepancy_open",
            "resolution_status",
            postgresql_where=text("resolution_status = 'Open'"),
        ),
    )


# Deferred imports
from app.models.department import Department  # noqa: E402, F401
from app.models.asset import Asset, AssetLocation  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
