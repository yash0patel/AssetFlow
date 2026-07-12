"""
app/models/asset.py
────────────────────
Module 3 — Asset Management (Registration & Directory)

Tables:
  asset_locations, assets, asset_status_history,
  asset_custom_attribute_values, asset_status_transition_rules
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
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
# Master: asset_locations (hierarchical)
# ──────────────────────────────────────────────────────────────────────────────
class AssetLocation(Base):
    __tablename__ = "asset_locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_type: Mapped[str] = mapped_column(String(30), nullable=False)
    parent_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_locations.id", ondelete="SET NULL"), nullable=True
    )
    address_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    parent_location: Mapped[Optional["AssetLocation"]] = relationship(
        "AssetLocation", remote_side="AssetLocation.id", foreign_keys=[parent_location_id]
    )
    child_locations: Mapped[list["AssetLocation"]] = relationship(
        "AssetLocation",
        foreign_keys=[parent_location_id],
        back_populates="parent_location",
        overlaps="parent_location",
    )
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="current_location")
    departments: Mapped[list["Department"]] = relationship(
        "Department",
        foreign_keys="Department.primary_location_id",
        back_populates="primary_location",
    )

    __table_args__ = (
        CheckConstraint(
            "location_type IN ('Site','Building','Floor','Room','Desk','Warehouse')",
            name="CK_asset_locations_type",
        ),
        Index("IDX_asset_locations_parent", "parent_location_id"),
        Index("IDX_asset_locations_type", "location_type"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Lookup: asset_status_transition_rules (data-driven state machine)
# ──────────────────────────────────────────────────────────────────────────────
class AssetStatusTransitionRule(Base):
    __tablename__ = "asset_status_transition_rules"

    from_status: Mapped[str] = mapped_column(String(20), primary_key=True)
    to_status: Mapped[str] = mapped_column(String(20), primary_key=True)
    requires_permission: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("permissions.name", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    required_permission: Mapped[Optional["Permission"]] = relationship(
        "Permission",
        foreign_keys=[requires_permission],
        back_populates="asset_status_transition_rules",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Master: assets — core, highest-traffic table
# ──────────────────────────────────────────────────────────────────────────────
class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    asset_tag: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False
    )
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    qr_code_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acquisition_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    acquisition_cost: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    condition: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Good", server_default="Good"
    )
    current_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Available", server_default="Available"
    )
    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_locations.id", ondelete="SET NULL"), nullable=True
    )
    owning_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized pointer maintained by trigger from asset_allocations
    current_holder_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    is_bookable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    warranty_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_retirement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="assets")
    current_location: Mapped[Optional["AssetLocation"]] = relationship(
        "AssetLocation", back_populates="assets"
    )
    owning_department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="assets"
    )
    current_holder_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", back_populates="held_assets"
    )
    created_by_user: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    status_history: Mapped[list["AssetStatusHistory"]] = relationship(
        "AssetStatusHistory", back_populates="asset"
    )
    allocations: Mapped[list["AssetAllocation"]] = relationship(
        "AssetAllocation", back_populates="asset"
    )
    transfer_requests: Mapped[list["AssetTransferRequest"]] = relationship(
        "AssetTransferRequest", back_populates="asset"
    )
    bookings: Mapped[list["ResourceBooking"]] = relationship(
        "ResourceBooking", back_populates="asset"
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="asset"
    )
    audit_items: Mapped[list["AuditCycleItem"]] = relationship(
        "AuditCycleItem", back_populates="asset"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        primaryjoin="and_(Attachment.entity_type=='Asset', Attachment.entity_id==Asset.id)",
        foreign_keys="Attachment.entity_id",
        viewonly=True,
    )
    custom_attribute_values: Mapped[list["AssetCustomAttributeValue"]] = relationship(
        "AssetCustomAttributeValue", back_populates="asset"
    )

    __table_args__ = (
        CheckConstraint(
            "condition IN ('New','Good','Fair','Poor','Damaged')", name="CK_assets_condition"
        ),
        CheckConstraint(
            "current_status IN ('Available','Allocated','Reserved','Under Maintenance','Lost','Retired','Disposed')",
            name="CK_assets_status",
        ),
        CheckConstraint("acquisition_cost >= 0", name="CK_assets_acquisition_cost_positive"),
        # Partial unique indexes
        Index(
            "UK_assets_serial",
            "serial_number",
            unique=True,
            postgresql_where=text("serial_number IS NOT NULL"),
        ),
        Index(
            "UK_assets_qr",
            "qr_code_value",
            unique=True,
            postgresql_where=text("qr_code_value IS NOT NULL"),
        ),
        Index("IDX_assets_category_status", "category_id", "current_status"),
        Index("IDX_assets_department_status", "owning_department_id", "current_status"),
        Index("IDX_assets_status", "current_status"),
        Index(
            "IDX_assets_bookable",
            "is_bookable",
            postgresql_where=text("is_bookable = TRUE"),
        ),
        Index(
            "IDX_assets_holder",
            "current_holder_employee_id",
            postgresql_where=text("current_holder_employee_id IS NOT NULL"),
        ),
        Index(
            "IDX_assets_retirement",
            "expected_retirement_date",
            postgresql_where=text("current_status NOT IN ('Retired','Disposed')"),
        ),
        # Covering index for Screen 4 list-view
        Index(
            "IDX_assets_directory_cover",
            "current_status",
            "category_id",
            postgresql_include=["id", "asset_tag", "name", "current_location_id"],
        ),
        # Full-text search index defined in migration (GIN on tsvector expression)
    )


# ──────────────────────────────────────────────────────────────────────────────
# History: asset_status_history (high-volume, append-only, range-partitioned)
# ──────────────────────────────────────────────────────────────────────────────
class AssetStatusHistory(Base):
    __tablename__ = "asset_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    previous_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="status_history")
    changed_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[changed_by])

    __table_args__ = (
        CheckConstraint(
            "reference_type IN ('Allocation','Booking','Maintenance','Audit','Manual')",
            name="CK_asset_status_history_reference_type",
        ),
        # Composite for per-asset history timeline
        Index("IDX_asset_status_history_asset", "asset_id", "changed_at"),
        Index("IDX_asset_status_history_changed_at", "changed_at"),
        Index("IDX_asset_status_history_reference", "reference_type", "reference_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Attribute values: asset_custom_attribute_values (EAV data side)
# ──────────────────────────────────────────────────────────────────────────────
class AssetCustomAttributeValue(Base):
    __tablename__ = "asset_custom_attribute_values"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
    )
    attribute_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_category_attributes.id", ondelete="CASCADE"),
        nullable=False,
    )
    value_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_number: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    value_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    value_boolean: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="custom_attribute_values")
    attribute: Mapped["AssetCategoryAttribute"] = relationship(
        "AssetCategoryAttribute", back_populates="values"
    )

    __table_args__ = (
        UniqueConstraint("asset_id", "attribute_id", name="UK_asset_attribute"),
        Index("IDX_attribute_values_attribute", "attribute_id"),
    )


# Deferred imports
from app.models.user import User, Permission  # noqa: E402, F401
from app.models.department import Department, AssetCategory, AssetCategoryAttribute  # noqa: E402, F401
from app.models.employee import Employee  # noqa: E402, F401
from app.models.allocation import AssetAllocation  # noqa: E402, F401
from app.models.transfer import AssetTransferRequest  # noqa: E402, F401
from app.models.booking import ResourceBooking  # noqa: E402, F401
from app.models.maintenance import MaintenanceRequest  # noqa: E402, F401
from app.models.audit import AuditCycleItem  # noqa: E402, F401
from app.models.shared import Attachment  # noqa: E402, F401
