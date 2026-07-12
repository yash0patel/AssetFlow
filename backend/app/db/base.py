"""
app/db/base.py
───────────────
Declarative base class for all SQLAlchemy ORM models.
All models must inherit from `Base` defined here.

Importing app.models here registers every table with Base.metadata
so Alembic autogenerate discovers all tables automatically.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base.
    All ORM models inherit from this class.
    """
    pass


# ---------------------------------------------------------------------------
# Import all model modules — side-effect registers every table with
# Base.metadata so Alembic autogenerate picks them all up.
# ---------------------------------------------------------------------------
import app.models  # noqa: E402, F401
