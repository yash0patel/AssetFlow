"""
app/models/user.py
──────────────────
Module 1 — Authentication & User Management

Tables:
  users, user_profiles, roles, permissions,
  user_roles, role_permissions,
  authentication_providers, user_auth_providers,
  user_sessions, devices, password_reset_tokens,
  login_attempts, user_verifications, user_status_history
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
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Lookup: roles
# ──────────────────────────────────────────────────────────────────────────────
class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="role"
    )

    __table_args__ = (
        Index("PK_roles", "id"),
        Index("UK_roles_name", "name", unique=True),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Lookup: permissions
# ──────────────────────────────────────────────────────────────────────────────
class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    module_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission"
    )
    asset_status_transition_rules: Mapped[list["AssetStatusTransitionRule"]] = relationship(
        "AssetStatusTransitionRule", back_populates="required_permission", foreign_keys="AssetStatusTransitionRule.requires_permission"
    )

    __table_args__ = (
        Index("PK_permissions", "id"),
        Index("UK_permissions_name", "name", unique=True),
        Index("IDX_permissions_module", "module_name"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Lookup: authentication_providers
# ──────────────────────────────────────────────────────────────────────────────
class AuthenticationProvider(Base):
    __tablename__ = "authentication_providers"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    user_auth_providers: Mapped[list["UserAuthProvider"]] = relationship(
        "UserAuthProvider", back_populates="provider"
    )

    __table_args__ = (Index("UK_auth_providers_name", "name", unique=True),)


# ──────────────────────────────────────────────────────────────────────────────
# Master: users
# ──────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Active",
        server_default="Active",
    )
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_login_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0")
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", foreign_keys="UserRole.user_id")
    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="user")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="user")
    login_attempts: Mapped[list["LoginAttempt"]] = relationship("LoginAttempt", back_populates="user")
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken", back_populates="user"
    )
    verifications: Mapped[list["UserVerification"]] = relationship(
        "UserVerification", back_populates="user"
    )
    status_history: Mapped[list["UserStatusHistory"]] = relationship(
        "UserStatusHistory", back_populates="user", foreign_keys="UserStatusHistory.user_id"
    )
    auth_providers: Mapped[list["UserAuthProvider"]] = relationship(
        "UserAuthProvider", back_populates="user"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="recipient_user"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="actor_user"
    )
    attachments_uploaded: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="uploaded_by_user"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Active','Inactive','Suspended','Deletion Pending','Deleted')",
            name="CK_users_status",
        ),
        # Lowercase email enforced at application layer; expression index done in migration
        Index("IDX_users_status", "status"),
        Index("IDX_users_locked", "locked_until", postgresql_where=text("locked_until IS NOT NULL")),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Master: user_profiles
# ──────────────────────────────────────────────────────────────────────────────
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("UK_user_profiles_user", "user_id", unique=True),
        Index("UK_user_profiles_phone", "phone_number", unique=True),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Junction: user_roles
# ──────────────────────────────────────────────────────────────────────────────
class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    department_scope_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_roles", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")
    assigner: Mapped["User"] = relationship("User", foreign_keys=[assigned_by])
    department_scope: Mapped[Optional["Department"]] = relationship(
        "Department", foreign_keys=[department_scope_id]
    )

    __table_args__ = (
        # Partial unique: one active role grant per (user, role, dept-scope)
        Index(
            "UK_user_roles_active",
            "user_id",
            "role_id",
            "department_scope_id",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
        Index("IDX_user_roles_user", "user_id"),
        Index("IDX_user_roles_role", "role_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Junction: role_permissions
# ──────────────────────────────────────────────────────────────────────────────
class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (Index("IDX_role_permissions_permission", "permission_id"),)


# ──────────────────────────────────────────────────────────────────────────────
# Junction: user_auth_providers
# ──────────────────────────────────────────────────────────────────────────────
class UserAuthProvider(Base):
    __tablename__ = "user_auth_providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("authentication_providers.id", ondelete="RESTRICT"), nullable=False
    )
    external_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="auth_providers")
    provider: Mapped["AuthenticationProvider"] = relationship(
        "AuthenticationProvider", back_populates="user_auth_providers"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "provider_id", name="UK_user_auth_providers"),
        Index("IDX_user_auth_providers_user", "user_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Security: user_sessions
# ──────────────────────────────────────────────────────────────────────────────
class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    access_token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
    device_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    device: Mapped[Optional["Device"]] = relationship("Device", back_populates="sessions")

    __table_args__ = (
        Index("IDX_user_sessions_user", "user_id"),
        Index(
            "IDX_user_sessions_active",
            "user_id",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Security: devices
# ──────────────────────────────────────────────────────────────────────────────
class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    device_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    is_trusted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="devices")
    sessions: Mapped[list["UserSession"]] = relationship("UserSession", back_populates="device")

    __table_args__ = (
        UniqueConstraint("user_id", "device_fingerprint", name="UK_devices_user_fingerprint"),
        Index("IDX_devices_user", "user_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Security: password_reset_tokens
# ──────────────────────────────────────────────────────────────────────────────
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")

    __table_args__ = (Index("IDX_password_reset_tokens_user", "user_id"),)


# ──────────────────────────────────────────────────────────────────────────────
# Security: login_attempts
# ──────────────────────────────────────────────────────────────────────────────
class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    was_successful: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="login_attempts")

    __table_args__ = (
        Index("IDX_login_attempts_email", "email", "attempted_at"),
        Index("IDX_login_attempts_user", "user_id"),
        Index("IDX_login_attempts_ip", "ip_address"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Verification: user_verifications (email only for v1)
# ──────────────────────────────────────────────────────────────────────────────
class UserVerification(Base):
    __tablename__ = "user_verifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    verification_type: Mapped[str] = mapped_column(String(20), nullable=False)
    verification_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="verifications")

    __table_args__ = (
        CheckConstraint("verification_type IN ('Email')", name="CK_user_verifications_type"),
        Index("UK_user_verifications_token", "verification_token", unique=True),
        Index("IDX_user_verifications_user", "user_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# History: user_status_history
# ──────────────────────────────────────────────────────────────────────────────
class UserStatusHistory(Base):
    __tablename__ = "user_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    previous_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="status_history", foreign_keys=[user_id]
    )
    changed_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[changed_by])

    __table_args__ = (Index("IDX_user_status_history_user", "user_id", "changed_at"),)


# Deferred imports to avoid circular references at module load
from app.models.notification import Notification  # noqa: E402, F401
from app.models.activity_log import ActivityLog  # noqa: E402, F401
from app.models.shared import Attachment  # noqa: E402, F401
from app.models.department import Department  # noqa: E402, F401
from app.models.asset import AssetStatusTransitionRule  # noqa: E402, F401
