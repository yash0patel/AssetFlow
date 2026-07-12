from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.allocation import AssetAllocation
from app.models.booking import ResourceBooking
from app.models.transfer import AssetTransferRequest
from app.models.maintenance import MaintenanceRequest


class DashboardService:

    async def get_kpis(self, db: AsyncSession) -> dict:
        # Asset counts by status
        stmt = select(Asset.current_status, func.count(Asset.id)).where(
            Asset.deleted_at.is_(None)
        ).group_by(Asset.current_status)
        res = await db.execute(stmt)
        status_counts = dict(res.all())

        # Active bookings
        active_bookings = (await db.execute(
            select(func.count(ResourceBooking.id)).where(ResourceBooking.status.in_(["Upcoming", "Ongoing"]))
        )).scalar_one()

        # Pending transfers
        pending_transfers = (await db.execute(
            select(func.count(AssetTransferRequest.id)).where(AssetTransferRequest.status == "Requested")
        )).scalar_one()

        # Overdue allocations
        today = datetime.now(timezone.utc).date()
        overdue_count = (await db.execute(
            select(func.count(AssetAllocation.id)).where(
                AssetAllocation.status == "Active",
                AssetAllocation.expected_return_date < today,
            )
        )).scalar_one()

        # Upcoming returns (within 7 days, not overdue)
        from datetime import timedelta
        in_7_days = today + timedelta(days=7)
        upcoming_returns = (await db.execute(
            select(func.count(AssetAllocation.id)).where(
                AssetAllocation.status == "Active",
                AssetAllocation.expected_return_date >= today,
                AssetAllocation.expected_return_date <= in_7_days,
            )
        )).scalar_one()

        # Maintenance today (approved/in-progress)
        maintenance_active = (await db.execute(
            select(func.count(MaintenanceRequest.id)).where(
                MaintenanceRequest.status.in_(["Approved", "Technician Assigned", "In Progress"])
            )
        )).scalar_one()

        return {
            "assets_available": status_counts.get("Available", 0),
            "assets_allocated": status_counts.get("Allocated", 0),
            "assets_under_maintenance": status_counts.get("Under Maintenance", 0),
            "active_bookings": active_bookings,
            "pending_transfers": pending_transfers,
            "upcoming_returns": upcoming_returns,
            "overdue_returns": overdue_count,
            "maintenance_active": maintenance_active,
        }

    async def get_overdue_allocations(self, db: AsyncSession) -> list:
        from sqlalchemy.orm import selectinload
        from app.models.employee import Employee
        from app.models.user import User

        today = datetime.now(timezone.utc).date()
        stmt = (
            select(AssetAllocation)
            .where(AssetAllocation.status == "Active", AssetAllocation.expected_return_date < today)
            .options(
                selectinload(AssetAllocation.asset),
                selectinload(AssetAllocation.allocated_to_employee).selectinload(Employee.user).selectinload(User.profile),
            )
            .order_by(AssetAllocation.expected_return_date)
            .limit(20)
        )
        res = await db.execute(stmt)
        allocs = res.scalars().all()

        result = []
        for a in allocs:
            holder = None
            if a.allocated_to_employee and a.allocated_to_employee.user and a.allocated_to_employee.user.profile:
                p = a.allocated_to_employee.user.profile
                holder = f"{p.first_name} {p.last_name or ''}".strip()
            result.append({
                "id": str(a.id),
                "asset_tag": a.asset.asset_tag if a.asset else None,
                "asset_name": a.asset.name if a.asset else None,
                "holder_name": holder,
                "expected_return_date": a.expected_return_date.isoformat() if a.expected_return_date else None,
                "days_overdue": (today - a.expected_return_date).days if a.expected_return_date else 0,
            })
        return result

    async def get_recent_activity(self, db: AsyncSession) -> list:
        from app.models.activity_log import ActivityLog
        from sqlalchemy.orm import selectinload
        from app.models.user import User, UserProfile

        stmt = (
            select(ActivityLog)
            .options(selectinload(ActivityLog.actor_user).selectinload(User.profile))
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
        )
        res = await db.execute(stmt)
        logs = res.scalars().all()

        result = []
        for log in logs:
            actor_name = log.actor_user.email if log.actor_user else "System"
            if log.actor_user and log.actor_user.profile:
                p = log.actor_user.profile
                actor_name = f"{p.first_name} {p.last_name or ''}".strip() or actor_name
            description = None
            if log.new_value and isinstance(log.new_value, dict):
                description = log.new_value.get("description", log.action)
            result.append({
                "id": log.id,
                "actor": actor_name,
                "action": log.action,
                "entity_type": log.entity_type,
                "description": description or log.action,
                "created_at": log.created_at.isoformat(),
            })
        return result


dashboard_service = DashboardService()
