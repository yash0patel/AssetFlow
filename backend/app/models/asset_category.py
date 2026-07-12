"""
app/models/asset_category.py
──────────────────────────────
Re-export pointer — asset categories live in department.py (Module 2 / Org Setup).
"""

from app.models.department import AssetCategory, AssetCategoryAttribute  # noqa: F401

__all__ = ["AssetCategory", "AssetCategoryAttribute"]
