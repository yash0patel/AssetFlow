"""
Initial migration: PostgreSQL extensions + exclusion constraint + expression indexes.

Revision: 001_initial_setup
"""
from alembic import op
import sqlalchemy as sa


revision = "001_initial_setup"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── PostgreSQL extensions ────────────────────────────────────────────────
    # pgcrypto provides gen_random_uuid() used as server_default for UUID PKs
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    # btree_gist required for the booking exclusion constraint
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # ── Case-insensitive email unique index ─────────────────────────────────
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS UK_users_email ON users (lower(email));"
    )

    # ── Asset full-text search index (GIN on tsvector) ──────────────────────
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS FTX_assets_search
        ON assets
        USING GIN (
            to_tsvector('simple',
                name || ' ' ||
                coalesce(serial_number, '') || ' ' ||
                asset_tag
            )
        );
        """
    )

    # ── pg_trgm fuzzy/partial match index for asset search ──────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS IDX_assets_name_trgm
        ON assets
        USING GIN (name gin_trgm_ops);
        """
    )

    # ── Resource bookings — exclusion constraint (overlap prevention) ────────
    # EXCLUDE USING gist prevents two bookings for the same asset
    # whose time ranges overlap, excluding Cancelled bookings.
    op.execute(
        """
        ALTER TABLE resource_bookings
        ADD CONSTRAINT EXCL_resource_bookings_no_overlap
        EXCLUDE USING gist (
            asset_id WITH =,
            tstzrange(start_datetime, end_datetime, '[)') WITH &&
        )
        WHERE (status <> 'Cancelled');
        """
    )

    # ── Asset category name case-insensitive unique index ────────────────────
    # (SQLAlchemy emits this via text() in the model; adding here as well
    #  for Alembic-managed environments that need explicit DDL)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS UK_asset_categories_name_lower "
        "ON asset_categories (lower(name));"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE resource_bookings DROP CONSTRAINT IF EXISTS EXCL_resource_bookings_no_overlap;"
    )
    op.execute("DROP INDEX IF EXISTS FTX_assets_search;")
    op.execute("DROP INDEX IF EXISTS IDX_assets_name_trgm;")
    op.execute("DROP INDEX IF EXISTS UK_users_email;")
    op.execute("DROP INDEX IF EXISTS UK_asset_categories_name_lower;")
