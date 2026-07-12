"""
app/db/base.py
───────────────
Declarative base class for all SQLAlchemy ORM models.
All models must inherit from `Base` defined here.
Import all model modules in this file so Alembic autogenerate works.
"""

from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from typing import Optional


class Base(DeclarativeBase):
    """
    Shared declarative base.

    All ORM models should inherit from this class.
    Common audit columns (created_at, updated_at) live here so every table
    automatically gets them.
    """

    # Subclasses override __tablename__
    pass


# ---------------------------------------------------------------------------
# Import all model modules here so that Alembic's autogenerate can discover
# every table. Uncomment each import as the model file is implemented.
# ---------------------------------------------------------------------------
# from app.models import user          # noqa: F401
# from app.models import department    # noqa: F401
# from app.models import employee      # noqa: F401
# from app.models import asset_category # noqa: F401
# from app.models import asset         # noqa: F401
# from app.models import allocation    # noqa: F401
# from app.models import transfer      # noqa: F401
# from app.models import booking       # noqa: F401
# from app.models import maintenance   # noqa: F401
# from app.models import audit         # noqa: F401
# from app.models import notification  # noqa: F401
# from app.models import activity_log  # noqa: F401
