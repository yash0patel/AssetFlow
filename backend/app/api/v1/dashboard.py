from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_kpis(db)


@router.get("/overdue-allocations")
async def get_overdue_allocations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_overdue_allocations(db)


@router.get("/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_recent_activity(db)
