"""
app/models/department.py
─────────────────────────
Module 2 — Organization Setup

Tables:
  departments, department_closure,
  asset_categories, asset_category_attributes
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Master: departments
# ──────────────────────────────────────────────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # Deferrable FK to employees — breaks the circular FK cycle at transaction level
    head_employee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL", deferrable=True, initially="DEFERRED"),
        nullable=True,
    )
    parent_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    primary_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_locations.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Active", server_default="Active"
    )
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
    head_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[head_employee_id], back_populates="headed_department"
    )
    parent_department: Mapped[Optional["Department"]] = relationship(
        "Department", remote_side="Department.id", foreign_keys=[parent_department_id]
    )
    sub_departments: Mapped[list["Department"]] = relationship(
        "Department",
        foreign_keys=[parent_department_id],
        back_populates="parent_department",
        overlaps="parent_department",
    )
    primary_location: Mapped[Optional["AssetLocation"]] = relationship(
        "AssetLocation", foreign_keys=[primary_location_id]
    )
    created_by_user: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    employees: Mapped[list["Employee"]] = relationship(
        "Employee", foreign_keys="Employee.department_id", back_populates="department"
    )
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="owning_department")
    user_roles: Mapped[list["UserRole"]] = relationship(
        "UserRole", foreign_keys="UserRole.department_scope_id", back_populates="department_scope"
    )
    # Closure table entries
    ancestor_paths: Mapped[list["DepartmentClosure"]] = relationship(
        "DepartmentClosure",
        foreign_keys="DepartmentClosure.descendant_id",
        back_populates="descendant",
    )
    descendant_paths: Mapped[list["DepartmentClosure"]] = relationship(
        "DepartmentClosure",
        foreign_keys="DepartmentClosure.ancestor_id",
        back_populates="ancestor",
    )

    __table_args__ = (
        CheckConstraint("status IN ('Active','Inactive')", name="CK_departments_status"),
        # Partial unique on code (only when code is not NULL)
        Index(
            "UK_departments_code",
            "code",
            unique=True,
            postgresql_where=text("code IS NOT NULL"),
        ),
        Index("IDX_departments_parent", "parent_department_id"),
        Index("IDX_departments_status", "status"),
        Index("IDX_departments_head", "head_employee_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Closure/Hierarchy: department_closure
# ──────────────────────────────────────────────────────────────────────────────
class DepartmentClosure(Base):
    __tablename__ = "department_closure"

    ancestor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    descendant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # 0 = self-row, 1 = direct parent, etc.
    depth: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Relationships
    ancestor: Mapped["Department"] = relationship(
        "Department",
        foreign_keys=[ancestor_id],
        back_populates="descendant_paths",
    )
    descendant: Mapped["Department"] = relationship(
        "Department",
        foreign_keys=[descendant_id],
        back_populates="ancestor_paths",
    )

    __table_args__ = (Index("IDX_dept_closure_descendant", "descendant_id"),)


# ──────────────────────────────────────────────────────────────────────────────
# Master: asset_categories
# ──────────────────────────────────────────────────────────────────────────────
class AssetCategory(Base):
    __tablename__ = "asset_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_useful_life_months: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    parent_category: Mapped[Optional["AssetCategory"]] = relationship(
        "AssetCategory",
        remote_side="AssetCategory.id",
        foreign_keys=[parent_category_id],
    )
    sub_categories: Mapped[list["AssetCategory"]] = relationship(
        "AssetCategory",
        foreign_keys=[parent_category_id],
        back_populates="parent_category",
        overlaps="parent_category",
    )
    attributes: Mapped[list["AssetCategoryAttribute"]] = relationship(
        "AssetCategoryAttribute", back_populates="category"
    )
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="category")

    __table_args__ = (
        # Case-insensitive unique via expression index — defined in migration
        Index("UK_asset_categories_name_lower", text("lower(name)"), unique=True),
        Index("IDX_asset_categories_parent", "parent_category_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Attribute definition: asset_category_attributes (EAV schema definition side)
# ──────────────────────────────────────────────────────────────────────────────
class AssetCategoryAttribute(Base):
    __tablename__ = "asset_category_attributes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asset_categories.id", ondelete="CASCADE"), nullable=False
    )
    attribute_key: Mapped[str] = mapped_column(String(50), nullable=False)
    attribute_label: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[str] = mapped_column(String(20), nullable=False)
    select_options: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0")
    )

    # Relationships
    category: Mapped["AssetCategory"] = relationship("AssetCategory", back_populates="attributes")
    values: Mapped[list["AssetCustomAttributeValue"]] = relationship(
        "AssetCustomAttributeValue", back_populates="attribute"
    )

    __table_args__ = (
        CheckConstraint(
            "data_type IN ('TEXT','NUMBER','DATE','BOOLEAN','SELECT')",
            name="CK_asset_category_attributes_data_type",
        ),
        UniqueConstraint("category_id", "attribute_key", name="UK_category_attribute"),
        Index("IDX_category_attributes_category", "category_id"),
    )


# Deferred imports to resolve forward references
from app.models.employee import Employee  # noqa: E402, F401
from app.models.asset import Asset, AssetLocation, AssetCustomAttributeValue  # noqa: E402, F401
from app.models.user import User, UserRole  # noqa: E402, F401
