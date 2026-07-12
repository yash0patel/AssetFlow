from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sequence import get_next_sequence_value
from app.models.maintenance import MaintenanceRequest
from app.repositories.asset_repository import asset_repo
from app.repositories.maintenance_repository import maintenance_repo
from app.services.asset_service import asset_service


class MaintenanceService:

    async def raise_request(
        self,
        db: AsyncSession,
        *,
        asset_id: UUID,
        raised_by_employee_id: UUID,
        issue_description: str,
        priority: str = "Medium",
    ) -> MaintenanceRequest:
        asset = await asset_repo.get(db, asset_id)
        if not asset or asset.deleted_at:
            raise HTTPException(status_code=404, detail="Asset not found.")

        code = await get_next_sequence_value(db, "MR")
        mr = MaintenanceRequest(
            request_code=code,
            asset_id=asset_id,
            raised_by_employee_id=raised_by_employee_id,
            issue_description=issue_description,
            priority=priority,
            status="Pending",
        )
        db.add(mr)
        await db.flush()
        return mr

    async def approve(
        self,
        db: AsyncSession,
        *,
        mr_id: UUID,
        approver_employee_id: UUID,
        technician_id: Optional[UUID] = None,
    ) -> MaintenanceRequest:
        mr = await maintenance_repo.get(db, mr_id)
        if not mr:
            raise HTTPException(status_code=404, detail="Maintenance request not found.")
        if mr.status != "Pending":
            raise HTTPException(status_code=400, detail=f"Cannot approve a request with status '{mr.status}'.")

        now = datetime.now(timezone.utc)
        mr.status = "Approved" if not technician_id else "Technician Assigned"
        mr.approved_by = approver_employee_id
        mr.approved_at = now
        mr.updated_at = now
        if technician_id:
            mr.technician_id = technician_id
            mr.assigned_at = now

        # Set asset to Under Maintenance
        asset = await asset_repo.get(db, mr.asset_id)
        if asset:
            await asset_service.change_status(
                db, asset, "Under Maintenance",
                remarks=f"Maintenance request {mr.request_code} approved",
                reference_type="Maintenance", reference_id=mr.id,
            )
        await db.flush()
        return mr

    async def reject(
        self,
        db: AsyncSession,
        *,
        mr_id: UUID,
        approver_employee_id: UUID,
        rejection_reason: str,
    ) -> MaintenanceRequest:
        mr = await maintenance_repo.get(db, mr_id)
        if not mr:
            raise HTTPException(status_code=404, detail="Maintenance request not found.")
        if mr.status != "Pending":
            raise HTTPException(status_code=400, detail=f"Cannot reject a request with status '{mr.status}'.")

        mr.status = "Rejected"
        mr.approved_by = approver_employee_id
        mr.approved_at = datetime.now(timezone.utc)
        mr.rejection_reason = rejection_reason
        mr.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return mr

    async def assign_technician(
        self,
        db: AsyncSession,
        *,
        mr_id: UUID,
        technician_id: UUID,
    ) -> MaintenanceRequest:
        mr = await maintenance_repo.get(db, mr_id)
        if not mr:
            raise HTTPException(status_code=404, detail="Maintenance request not found.")
        if mr.status not in ("Approved",):
            raise HTTPException(status_code=400, detail=f"Cannot assign technician with status '{mr.status}'.")

        mr.technician_id = technician_id
        mr.assigned_at = datetime.now(timezone.utc)
        mr.status = "Technician Assigned"
        mr.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return mr

    async def start(self, db: AsyncSession, *, mr_id: UUID) -> MaintenanceRequest:
        mr = await maintenance_repo.get(db, mr_id)
        if not mr:
            raise HTTPException(status_code=404, detail="Maintenance request not found.")
        if mr.status not in ("Approved", "Technician Assigned"):
            raise HTTPException(status_code=400, detail=f"Cannot start with status '{mr.status}'.")
        mr.status = "In Progress"
        mr.started_at = datetime.now(timezone.utc)
        mr.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return mr

    async def resolve(
        self,
        db: AsyncSession,
        *,
        mr_id: UUID,
        resolution_notes: Optional[str] = None,
        actual_cost: Optional[float] = None,
    ) -> MaintenanceRequest:
        mr = await maintenance_repo.get(db, mr_id)
        if not mr:
            raise HTTPException(status_code=404, detail="Maintenance request not found.")
        if mr.status not in ("In Progress", "Technician Assigned", "Approved"):
            raise HTTPException(status_code=400, detail=f"Cannot resolve with status '{mr.status}'.")

        now = datetime.now(timezone.utc)
        mr.status = "Resolved"
        mr.resolved_at = now
        mr.resolution_notes = resolution_notes
        mr.actual_cost = actual_cost
        mr.updated_at = now

        # Return asset to Available
        asset = await asset_repo.get(db, mr.asset_id)
        if asset:
            await asset_service.change_status(
                db, asset, "Available",
                remarks=f"Maintenance resolved: {resolution_notes or ''}",
                reference_type="Maintenance", reference_id=mr.id,
            )
        await db.flush()
        return mr


maintenance_service = MaintenanceService()
