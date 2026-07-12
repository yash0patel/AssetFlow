from fastapi import APIRouter, Depends
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.asset import Asset
from app.models.allocation import AssetAllocation
from app.models.maintenance import MaintenanceRequest
from app.models.department import Department

router = APIRouter()


@router.get("/asset-utilization")
async def asset_utilization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Asset count by status."""
    stmt = select(Asset.current_status, func.count(Asset.id)).where(
        Asset.deleted_at.is_(None)
    ).group_by(Asset.current_status)
    res = await db.execute(stmt)
    return [{"name": row[0], "value": row[1]} for row in res.all()]


@router.get("/department-allocation-summary")
async def department_allocation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Active allocations per department."""
    stmt = (
        select(Department.name, func.count(AssetAllocation.id))
        .join(AssetAllocation, AssetAllocation.allocated_to_department_id == Department.id, isouter=True)
        .where(AssetAllocation.status == "Active")
        .group_by(Department.name)
        .order_by(func.count(AssetAllocation.id).desc())
    )
    res = await db.execute(stmt)
    return [{"name": row[0], "value": row[1]} for row in res.all()]


@router.get("/maintenance-frequency")
async def maintenance_frequency(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Maintenance request count by month (last 6 months)."""
    from sqlalchemy import text
    stmt = text("""
        SELECT TO_CHAR(created_at, 'Mon') as month,
               EXTRACT(MONTH FROM created_at) as month_num,
               COUNT(*) as count
        FROM maintenance_requests
        WHERE created_at >= NOW() - INTERVAL '6 months'
        GROUP BY month, month_num
        ORDER BY month_num
    """)
    res = await db.execute(stmt)
    return [{"month": row[0], "count": row[2]} for row in res.all()]


@router.get("/assets-near-retirement")
async def assets_near_retirement(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assets with retirement date within 90 days."""
    from datetime import datetime, timezone, timedelta
    today = datetime.now(timezone.utc).date()
    in_90 = today + timedelta(days=90)
    stmt = (
        select(Asset)
        .where(
            Asset.deleted_at.is_(None),
            Asset.expected_retirement_date != None,
            Asset.expected_retirement_date <= in_90,
            Asset.expected_retirement_date >= today,
        )
        .order_by(Asset.expected_retirement_date)
        .limit(20)
    )
    from sqlalchemy.orm import selectinload
    from app.models.department import AssetCategory
    stmt = stmt.options(selectinload(Asset.category))
    res = await db.execute(stmt)
    assets = res.scalars().all()
    return [
        {
            "id": str(a.id),
            "asset_tag": a.asset_tag,
            "name": a.name,
            "category": a.category.name if a.category else None,
            "expected_retirement_date": a.expected_retirement_date.isoformat(),
            "days_remaining": (a.expected_retirement_date - today).days,
        }
        for a in assets
    ]
