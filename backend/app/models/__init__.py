"""
app/models/__init__.py
───────────────────────
Central export for all ORM models.
Import order matters — base models first, dependent models later.
"""

# Module 9 (shared) — no FK deps on other modules
from app.models.shared import Attachment, EntityCodeSequence  # noqa: F401

# Module 8 — depends only on users
from app.models.notification import Notification, NotificationPreference  # noqa: F401
from app.models.activity_log import ActivityLog  # noqa: F401

# Module 1 — auth (users dep on notification/activity_log via back_populates)
from app.models.user import (  # noqa: F401
    User,
    UserProfile,
    Role,
    Permission,
    UserRole,
    RolePermission,
    AuthenticationProvider,
    UserAuthProvider,
    UserSession,
    Device,
    PasswordResetToken,
    LoginAttempt,
    UserVerification,
    UserStatusHistory,
)

# Module 3 — assets (locations needed before departments FK)
from app.models.asset import (  # noqa: F401
    AssetLocation,
    AssetStatusTransitionRule,
    Asset,
    AssetStatusHistory,
    AssetCustomAttributeValue,
)

# Module 2 — org setup (departments dep on asset_locations; employees dep on departments)
from app.models.department import (  # noqa: F401
    Department,
    DepartmentClosure,
    AssetCategory,
    AssetCategoryAttribute,
)
from app.models.employee import Employee  # noqa: F401

# Module 4 — allocation & transfer
from app.models.allocation import AssetAllocation  # noqa: F401
from app.models.transfer import AssetTransferRequest  # noqa: F401

# Module 5 — booking
from app.models.booking import ResourceBooking  # noqa: F401

# Module 6 — maintenance
from app.models.maintenance import (  # noqa: F401
    MaintenanceTechnician,
    MaintenanceRequest,
    MaintenanceStatusHistory,
)

# Module 7 — audit
from app.models.audit import (  # noqa: F401
    AuditCycle,
    AuditCycleAuditor,
    AuditCycleItem,
    AuditDiscrepancyReport,
)

# Module 10 — OLAP star schema
from app.models.analytics import (  # noqa: F401
    DimDate,
    DimTimeOfDay,
    DimAsset,
    DimDepartment,
    DimEmployee,
    DimCategory,
    FactAssetUtilization,
    FactResourceBooking,
    FactMaintenance,
    FactAllocation,
)
