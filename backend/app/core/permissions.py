"""
app/core/permissions.py
────────────────────────
Role constants and permission stubs.
Implement permission-checking logic here when business logic phase begins.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles within the AssetFlow ERP."""

    ADMIN = "admin"
    ASSET_MANAGER = "asset_manager"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


# Ordered privilege levels — higher index = more privileges
ROLE_HIERARCHY: list[UserRole] = [
    UserRole.EMPLOYEE,
    UserRole.DEPARTMENT_HEAD,
    UserRole.ASSET_MANAGER,
    UserRole.ADMIN,
]


def has_minimum_role(user_role: UserRole, required_role: UserRole) -> bool:
    """Return True if *user_role* meets or exceeds *required_role*."""
    return ROLE_HIERARCHY.index(user_role) >= ROLE_HIERARCHY.index(required_role)
