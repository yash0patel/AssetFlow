from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.allocation import AssetAllocation
from app.models.asset import Asset
from app.models.transfer import AssetTransferRequest
from app.repositories.allocation_repository import allocation_repo
from app.repositories.asset_repository import asset_repo
from app.services.asset_service import asset_service


class AllocationService:
    """Business logic for Asset Allocation & Transfer (Screen 5)."""

    async def allocate(
        self,
        db: AsyncSession,
        *,
        asset_id: UUID,
        allocator_employee_id: UUID,
        to_employee_id: Optional[UUID] = None,
        to_department_id: Optional[UUID] = None,
        expected_return_date=None,
    ) -> AssetAllocation:
        # Validate exactly one target
        if not to_employee_id and not to_department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must specify either employee or department as the allocation target.",
            )
        if to_employee_id and to_department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot allocate to both employee and department simultaneously.",
            )

        # Load asset
        asset = await asset_repo.get(db, asset_id)
        if not asset or asset.deleted_at:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")

        # Block if asset already has an active allocation
        existing = await allocation_repo.get_active_allocation_for_asset(db, asset_id)
        if existing:
            holder_name = "another department"
            if existing.allocated_to_employee and existing.allocated_to_employee.user:
                p = existing.allocated_to_employee.user.profile
                holder_name = f"{p.first_name} {p.last_name or ''}".strip() if p else holder_name
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset is currently held by {holder_name}. Submit a transfer request instead.",
            )

        # Create allocation
        alloc = AssetAllocation(
            asset_id=asset_id,
            allocated_to_employee_id=to_employee_id,
            allocated_to_department_id=to_department_id,
            allocated_by=allocator_employee_id,
            expected_return_date=expected_return_date,
            status="Active",
        )
        db.add(alloc)
        await db.flush()

        # Update asset status and holder
        asset.current_status = "Allocated"
        asset.current_holder_employee_id = to_employee_id
        asset.updated_at = datetime.now(timezone.utc)
        await asset_repo.add_status_history(
            db,
            asset_id=asset_id,
            previous_status="Available",
            new_status="Allocated",
            changed_by=None,
            remarks="Asset allocated",
            reference_type="Allocation",
            reference_id=alloc.id,
        )
        await db.flush()
        return alloc

    async def return_asset(
        self,
        db: AsyncSession,
        *,
        allocation_id: UUID,
        returned_by_employee_id: UUID,
        return_condition: str = "Good",
        return_notes: Optional[str] = None,
    ) -> AssetAllocation:
        alloc = await allocation_repo.get_by_id_with_relations(db, allocation_id)
        if not alloc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allocation not found.")
        if alloc.status != "Active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Allocation is not active.")

        now = datetime.now(timezone.utc)
        alloc.status = "Returned"
        alloc.actual_return_date = now
        alloc.return_condition = return_condition
        alloc.return_notes = return_notes
        alloc.returned_by = returned_by_employee_id
        alloc.updated_at = now

        # Revert asset status
        asset = alloc.asset
        asset.current_status = "Available"
        asset.current_holder_employee_id = None
        asset.updated_at = now
        await asset_repo.add_status_history(
            db,
            asset_id=asset.id,
            previous_status="Allocated",
            new_status="Available",
            changed_by=None,
            remarks=f"Returned. Condition: {return_condition}. {return_notes or ''}".strip(),
            reference_type="Allocation",
            reference_id=allocation_id,
        )
        await db.flush()
        return alloc

    async def create_transfer_request(
        self,
        db: AsyncSession,
        *,
        asset_id: UUID,
        requester_employee_id: UUID,
        to_employee_id: UUID,
        reason: Optional[str] = None,
    ) -> AssetTransferRequest:
        # Must have an active allocation
        alloc = await allocation_repo.get_active_allocation_for_asset(db, asset_id)
        if not alloc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Asset has no active allocation to transfer from.")

        tr = AssetTransferRequest(
            asset_id=asset_id,
            current_allocation_id=alloc.id,
            from_employee_id=alloc.allocated_to_employee_id,
            to_employee_id=to_employee_id,
            requested_by=requester_employee_id,
            reason=reason or "Transfer requested",
            status="Requested",
        )
        db.add(tr)
        await db.flush()
        return tr

    async def approve_transfer(
        self,
        db: AsyncSession,
        *,
        transfer_id: UUID,
        approver_employee_id: UUID,
    ) -> AssetTransferRequest:
        from app.repositories.transfer_repository import transfer_repo
        tr = await transfer_repo.get_by_id_with_relations(db, transfer_id)
        if not tr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer request not found.")
        if tr.status != "Requested":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Transfer is already {tr.status}.")

        now = datetime.now(timezone.utc)
        # Mark old allocation as returned
        old_alloc = await allocation_repo.get_by_id_with_relations(db, tr.current_allocation_id)
        if old_alloc and old_alloc.status == "Active":
            old_alloc.status = "Returned"
            old_alloc.actual_return_date = now
            old_alloc.updated_at = now

        # Create new allocation for the transfer recipient
        new_alloc = AssetAllocation(
            asset_id=tr.asset_id,
            allocated_to_employee_id=tr.to_employee_id,
            allocated_by=approver_employee_id,
            status="Active",
        )
        db.add(new_alloc)
        await db.flush()

        # Update asset holder
        asset = await asset_repo.get(db, tr.asset_id)
        if asset:
            asset.current_holder_employee_id = tr.to_employee_id
            asset.updated_at = now

        tr.status = "Completed"
        tr.approved_by = approver_employee_id
        tr.approved_at = now
        tr.completed_at = now
        tr.updated_at = now
        await db.flush()
        return tr

    async def reject_transfer(
        self,
        db: AsyncSession,
        *,
        transfer_id: UUID,
        approver_employee_id: UUID,
        rejection_reason: Optional[str] = None,
    ) -> AssetTransferRequest:
        from app.repositories.transfer_repository import transfer_repo
        tr = await transfer_repo.get_by_id_with_relations(db, transfer_id)
        if not tr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer request not found.")
        if tr.status != "Requested":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Transfer is already {tr.status}.")
        tr.status = "Rejected"
        tr.approved_by = approver_employee_id
        tr.approved_at = datetime.now(timezone.utc)
        tr.rejection_reason = rejection_reason
        tr.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return tr


allocation_service = AllocationService()
