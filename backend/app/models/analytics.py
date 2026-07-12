"""
app/models/analytics.py
────────────────────────
Module 10 — Reports & Analytics (OLAP Star Schema)

Tables:
  dim_date, dim_time_of_day,
  dim_asset (SCD Type 2), dim_department, dim_employee, dim_category,
  fact_asset_utilization, fact_resource_bookings, fact_maintenance, fact_allocation

These tables are fed by CDC/ETL from OLTP — never written to directly
by transactional endpoints. Physically/logically separate from all OLTP modules.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_date (pre-populated 2020–2035)
# ──────────────────────────────────────────────────────────────────────────────
class DimDate(Base):
    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True)  # YYYYMMDD
    full_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_weekend: Mapped[bool] = mapped_column(Boolean, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    quarter: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (Index("IDX_dim_date_full_date", "full_date"),)


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_time_of_day (for booking heatmaps)
# ──────────────────────────────────────────────────────────────────────────────
class DimTimeOfDay(Base):
    __tablename__ = "dim_time_of_day"

    time_key: Mapped[int] = mapped_column(SmallInteger, primary_key=True)  # 0–23 hour bucket
    hour_label: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g. "09:00"
    is_business_hour: Mapped[bool] = mapped_column(Boolean, nullable=False)


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_asset (SCD Type 2)
# ──────────────────────────────────────────────────────────────────────────────
class DimAsset(Base):
    __tablename__ = "dim_asset"

    asset_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )  # Natural key → OLTP assets.id
    asset_tag: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)   # Denormalized
    department_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)  # Denormalized
    acquisition_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(14, 2), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # NULL = current version
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("IDX_dim_asset_natural", "asset_id", "is_current"),
        Index(
            "IDX_dim_asset_current",
            "asset_id",
            postgresql_where=text("is_current = TRUE"),
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_department (SCD Type 2)
# ──────────────────────────────────────────────────────────────────────────────
class DimDepartment(Base):
    __tablename__ = "dim_department"

    department_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("IDX_dim_department_natural", "department_id", "is_current"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_employee (SCD Type 2)
# ──────────────────────────────────────────────────────────────────────────────
class DimEmployee(Base):
    __tablename__ = "dim_employee"

    employee_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    employee_code: Mapped[str] = mapped_column(String(20), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    department_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("IDX_dim_employee_natural", "employee_id", "is_current"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Dimension: dim_category (SCD Type 2)
# ──────────────────────────────────────────────────────────────────────────────
class DimCategory(Base):
    __tablename__ = "dim_category"

    category_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("IDX_dim_category_natural", "category_id", "is_current"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fact: fact_asset_utilization (grain: 1 row per asset per day)
# Powers "Most used assets" / "Idle assets" (Screen 9)
# ──────────────────────────────────────────────────────────────────────────────
class FactAssetUtilization(Base):
    __tablename__ = "fact_asset_utilization"

    date_key: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_date.date_key"), primary_key=True
    )
    asset_sk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_asset.asset_sk"), primary_key=True
    )
    department_sk: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dim_department.department_sk"), nullable=True
    )
    is_allocated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_idle: Mapped[bool] = mapped_column(Boolean, nullable=False)
    days_since_last_use: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    booking_hours: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(5, 2), nullable=True
    )  # Bookable assets only

    __table_args__ = (
        Index("IDX_fact_utilization_date", "date_key"),
        Index("IDX_fact_utilization_asset", "asset_sk"),
        Index("IDX_fact_utilization_dept", "department_sk"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fact: fact_resource_bookings (grain: 1 row per booking)
# Powers booking heatmap: GROUP BY start_time_key, day_of_week
# ──────────────────────────────────────────────────────────────────────────────
class FactResourceBooking(Base):
    __tablename__ = "fact_resource_bookings"

    booking_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )  # Natural key → OLTP resource_bookings.id
    date_key: Mapped[int] = mapped_column(Integer, ForeignKey("dim_date.date_key"), nullable=False)
    start_time_key: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_time_of_day.time_key"), nullable=False
    )
    asset_sk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_asset.asset_sk"), nullable=False
    )
    department_sk: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dim_department.department_sk"), nullable=True
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        Index("IDX_fact_bookings_date", "date_key"),
        Index("IDX_fact_bookings_asset", "asset_sk"),
        Index("IDX_fact_bookings_heatmap", "start_time_key", "date_key"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fact: fact_maintenance (grain: 1 row per maintenance request)
# Powers "Maintenance Frequency" trend and cost analysis
# ──────────────────────────────────────────────────────────────────────────────
class FactMaintenance(Base):
    __tablename__ = "fact_maintenance"

    maintenance_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    maintenance_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )  # Natural key → OLTP maintenance_requests.id
    date_key: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_date.date_key"), nullable=False
    )  # Request-raised date
    asset_sk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_asset.asset_sk"), nullable=False
    )
    category_sk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_category.category_sk"), nullable=False
    )
    days_to_approve: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_to_resolve: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_cost: Mapped[Optional[Numeric]] = mapped_column(Numeric(12, 2), nullable=True)

    __table_args__ = (
        Index("IDX_fact_maintenance_date", "date_key"),
        Index("IDX_fact_maintenance_asset", "asset_sk"),
        Index("IDX_fact_maintenance_category", "category_sk"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fact: fact_allocation (grain: 1 row per allocation period)
# Powers "Department-wise allocation summary"
# ──────────────────────────────────────────────────────────────────────────────
class FactAllocation(Base):
    __tablename__ = "fact_allocation"

    allocation_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    allocation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )  # Natural key → OLTP asset_allocations.id
    start_date_key: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_date.date_key"), nullable=False
    )
    end_date_key: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dim_date.date_key"), nullable=True
    )  # NULL = still active
    asset_sk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_asset.asset_sk"), nullable=False
    )
    department_sk: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dim_department.department_sk"), nullable=True
    )
    duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("IDX_fact_allocation_start_date", "start_date_key"),
        Index("IDX_fact_allocation_asset", "asset_sk"),
        Index("IDX_fact_allocation_dept", "department_sk"),
    )
