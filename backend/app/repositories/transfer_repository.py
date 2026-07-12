from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transfer import AssetTransferRequest
from app.models.employee import Employee
from app.models.user import User, UserProfile
from app.repositories.base_repository import BaseRepository


class TransferRepository(BaseRepository[AssetTransferRequest]):
    def __init__(self):
        super().__init__(AssetTransferRequest)

    async def get_by_id_with_relations(self, db: AsyncSession, transfer_id: UUID) -> Optional[AssetTransferRequest]:
        stmt = (
            select(AssetTransferRequest)
            .where(AssetTransferRequest.id == transfer_id)
            .options(
                selectinload(AssetTransferRequest.asset),
                selectinload(AssetTransferRequest.from_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AssetTransferRequest.to_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AssetTransferRequest.requester).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AssetTransferRequest.approver).selectinload(Employee.user).selectinload(User.profile),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_transfers(
        self,
        db: AsyncSession,
        *,
        asset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AssetTransferRequest], int]:
        stmt = select(AssetTransferRequest)
        if asset_id:
            stmt = stmt.where(AssetTransferRequest.asset_id == asset_id)
        if status:
            stmt = stmt.where(AssetTransferRequest.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(AssetTransferRequest.asset),
            selectinload(AssetTransferRequest.from_employee).selectinload(Employee.user).selectinload(User.profile),
            selectinload(AssetTransferRequest.to_employee).selectinload(Employee.user).selectinload(User.profile),
            selectinload(AssetTransferRequest.requester).selectinload(Employee.user).selectinload(User.profile),
        ).order_by(AssetTransferRequest.created_at.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total


transfer_repo = TransferRepository()
