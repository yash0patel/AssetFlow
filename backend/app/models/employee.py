"""
app/models/employee.py
───────────────────────
Module 2 — Organization Setup (Employee)

Tables:
  employees
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
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Master: employees
# ──────────────────────────────────────────────────────────────────────────────
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    employee_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    # Deferrable FK to departments — breaks the circular FK cycle
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL", deferrable=True, initially="DEFERRED"),
        nullable=True,
    )
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reporting_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    date_of_joining: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Active", server_default="Active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    department: Mapped[Optional["Department"]] = relationship(
        "Department", foreign_keys=[department_id], back_populates="employees"
    )
    headed_department: Mapped[Optional["Department"]] = relationship(
        "Department",
        foreign_keys="Department.head_employee_id",
        back_populates="head_employee",
        uselist=False,
    )
    reporting_manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", remote_side="Employee.id", foreign_keys=[reporting_manager_id]
    )
    direct_reports: Mapped[list["Employee"]] = relationship(
        "Employee",
        foreign_keys=[reporting_manager_id],
        back_populates="reporting_manager",
        overlaps="reporting_manager",
    )
    # Assets currently held (denormalized pointer)
    held_assets: Mapped[list["Asset"]] = relationship(
        "Asset", back_populates="current_holder_employee"
    )
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        "AssetAllocation",
        foreign_keys="AssetAllocation.allocated_to_employee_id",
        back_populates="allocated_to_employee",
    )
    bookings: Mapped[list["ResourceBooking"]] = relationship(
        "ResourceBooking",
        foreign_keys="ResourceBooking.booked_by_employee_id",
        back_populates="booked_by_employee",
    )
    maintenance_requests_raised: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest",
        foreign_keys="MaintenanceRequest.raised_by_employee_id",
        back_populates="raised_by_employee",
    )
    audit_assignments: Mapped[list["AuditCycleAuditor"]] = relationship(
        "AuditCycleAuditor", back_populates="employee"
    )

    __table_args__ = (
        CheckConstraint("status IN ('Active','Inactive')", name="CK_employees_status"),
        Index("UK_employees_user", "user_id", unique=True),
        Index("UK_employees_code", "employee_code", unique=True),
        Index("IDX_employees_department", "department_id"),
        Index("IDX_employees_manager", "reporting_manager_id"),
        Index("IDX_employees_status", "status"),
        # Covering index for "active employees in department" picker
        Index(
            "IDX_employees_search",
            "department_id",
            "status",
            postgresql_include=["id", "employee_code"],
        ),
    )


# Deferred imports
from app.models.user import User  # noqa: E402, F401
from app.models.department import Department  # noqa: E402, F401
from app.models.asset import Asset  # noqa: E402, F401
from app.models.allocation import AssetAllocation  # noqa: E402, F401
from app.models.booking import ResourceBooking  # noqa: E402, F401
from app.models.maintenance import MaintenanceRequest  # noqa: E402, F401
from app.models.audit import AuditCycleAuditor  # noqa: E402, F401
