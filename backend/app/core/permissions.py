"""
app/core/permissions.py
────────────────────────
Role constants and permission stubs.
Implement permission-checking logic here when business logic phase begins.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles within the AssetFlow ERP."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    AUDITOR = "auditor"
    VIEWER = "viewer"


# Ordered privilege levels — higher index = more privileges
ROLE_HIERARCHY: list[UserRole] = [
    UserRole.VIEWER,
    UserRole.EMPLOYEE,
    UserRole.AUDITOR,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.SUPER_ADMIN,
]


def has_minimum_role(user_role: UserRole, required_role: UserRole) -> bool:
    """Return True if *user_role* meets or exceeds *required_role*."""
    return ROLE_HIERARCHY.index(user_role) >= ROLE_HIERARCHY.index(required_role)
