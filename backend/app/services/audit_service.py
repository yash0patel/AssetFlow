from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditCycle, AuditCycleAuditor, AuditCycleItem, AuditDiscrepancyReport
from app.repositories.audit_repository import audit_repo
from app.repositories.asset_repository import asset_repo
from app.services.asset_service import asset_service


class AuditService:

    async def create_cycle(
        self,
        db: AsyncSession,
        *,
        cycle_name: str,
        start_date,
        end_date,
        creator_employee_id: UUID,
        scope_department_id: Optional[UUID] = None,
        scope_location_id: Optional[UUID] = None,
        auditor_ids: List[UUID] = [],
    ) -> AuditCycle:
        if end_date < start_date:
            raise HTTPException(status_code=400, detail="end_date must be on or after start_date.")

        cycle = AuditCycle(
            cycle_name=cycle_name,
            start_date=start_date,
            end_date=end_date,
            created_by=creator_employee_id,
            scope_department_id=scope_department_id,
            scope_location_id=scope_location_id,
            status="Planned",
        )
        db.add(cycle)
        await db.flush()

        # Add auditors
        for emp_id in auditor_ids:
            auditor = AuditCycleAuditor(audit_cycle_id=cycle.id, employee_id=emp_id)
            db.add(auditor)

        # Pre-populate items: pull all non-deleted assets matching scope
        from sqlalchemy import select
        from app.models.asset import Asset
        stmt = select(Asset).where(Asset.deleted_at.is_(None))
        if scope_department_id:
            stmt = stmt.where(Asset.owning_department_id == scope_department_id)
        if scope_location_id:
            stmt = stmt.where(Asset.current_location_id == scope_location_id)
        res = await db.execute(stmt)
        assets = res.scalars().all()

        for a in assets:
            item = AuditCycleItem(
                audit_cycle_id=cycle.id,
                asset_id=a.id,
                verification_status="Pending",
            )
            db.add(item)

        cycle.status = "In Progress"
        await db.flush()
        return cycle

    async def verify_item(
        self,
        db: AsyncSession,
        *,
        item_id: int,
        verifier_employee_id: UUID,
        verification_status: str,
        remarks: Optional[str] = None,
    ) -> AuditCycleItem:
        item = await audit_repo.get_item(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Audit item not found.")

        item.verification_status = verification_status
        item.verified_by = verifier_employee_id
        item.verified_at = datetime.now(timezone.utc)
        item.remarks = remarks

        # Auto-generate discrepancy report for Missing/Damaged
        if verification_status in ("Missing", "Damaged"):
            report = AuditDiscrepancyReport(
                audit_cycle_id=item.audit_cycle_id,
                audit_cycle_item_id=item.id,
                asset_id=item.asset_id,
                discrepancy_type=verification_status,
                resolution_status="Open",
            )
            db.add(report)
        await db.flush()
        return item

    async def close_cycle(
        self,
        db: AsyncSession,
        *,
        cycle_id: UUID,
        closer_employee_id: UUID,
    ) -> AuditCycle:
        cycle = await audit_repo.get_by_id_with_relations(db, cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="Audit cycle not found.")
        if cycle.status == "Closed":
            raise HTTPException(status_code=400, detail="Audit cycle is already closed.")

        now = datetime.now(timezone.utc)
        cycle.status = "Closed"
        cycle.closed_by = closer_employee_id
        cycle.closed_at = now
        cycle.updated_at = now

        # Update confirmed-missing assets to Lost
        from sqlalchemy import select
        from app.models.audit import AuditDiscrepancyReport
        stmt = select(AuditDiscrepancyReport).where(
            AuditDiscrepancyReport.audit_cycle_id == cycle_id,
            AuditDiscrepancyReport.discrepancy_type == "Missing",
            AuditDiscrepancyReport.resolution_status == "Open",
        )
        res = await db.execute(stmt)
        open_missing = res.scalars().all()
        for rep in open_missing:
            asset = await asset_repo.get(db, rep.asset_id)
            if asset:
                await asset_service.change_status(
                    db, asset, "Lost",
                    remarks=f"Confirmed missing in audit cycle {cycle.cycle_name}",
                    reference_type="Audit", reference_id=cycle_id,
                )

        await db.flush()
        return cycle


audit_service = AuditService()
