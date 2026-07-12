"""
app/models/shared.py
─────────────────────
Module 9 — Shared / Common (Cross-Cutting Infrastructure)

Tables:
  attachments, entity_code_sequences
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
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ──────────────────────────────────────────────────────────────────────────────
# Shared: attachments (polymorphic — replaces per-module attachment tables)
# ──────────────────────────────────────────────────────────────────────────────
class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    # Polymorphic discriminator — not a DB-enforced FK; integrity via app + orphan-check job
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    file_type: Mapped[str] = mapped_column(String(15), nullable=False)
    # Object storage URL (S3/GCS) — files never stored as DB blobs
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    uploaded_by_user: Mapped["User"] = relationship(
        "User", back_populates="attachments_uploaded"
    )

    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('Asset','MaintenanceRequest','AuditCycleItem','TransferRequest')",
            name="CK_attachments_entity_type",
        ),
        CheckConstraint(
            "file_type IN ('Photo','Document')", name="CK_attachments_file_type"
        ),
        # Standard polymorphic lookup
        Index("IDX_attachments_entity", "entity_type", "entity_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Shared: entity_code_sequences
# Collision-proof generator for human-readable business IDs (AF-0114, EMP-00042, MR-00231)
# ──────────────────────────────────────────────────────────────────────────────
class EntityCodeSequence(Base):
    __tablename__ = "entity_code_sequences"

    # e.g. 'AF', 'EMP', 'MR', 'BK'
    entity_prefix: Mapped[str] = mapped_column(String(10), primary_key=True)
    current_value: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default=text("0")
    )
    padding_length: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=4, server_default=text("4")
    )


# Deferred imports
from app.models.user import User  # noqa: E402, F401
