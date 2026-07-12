from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sequence import get_next_sequence_value
from app.models.asset import Asset
from app.repositories.asset_repository import asset_repo


class AssetService:
    """Business logic for Asset Registration & Directory (Screen 4)."""

    async def create_asset(
        self,
        db: AsyncSession,
        *,
        name: str,
        category_id: UUID,
        serial_number: Optional[str],
        description: Optional[str],
        acquisition_date,
        acquisition_cost,
        condition: str,
        location_id: Optional[UUID],
        department_id: Optional[UUID],
        is_bookable: bool,
        warranty_expiry_date,
        expected_retirement_date,
        created_by: UUID,
    ) -> Asset:
        # Generate auto asset tag
        asset_tag = await get_next_sequence_value(db, "AF")

        asset = Asset(
            asset_tag=asset_tag,
            name=name,
            category_id=category_id,
            serial_number=serial_number or None,
            description=description or None,
            acquisition_date=acquisition_date,
            acquisition_cost=acquisition_cost,
            condition=condition,
            current_status="Available",
            current_location_id=location_id,
            owning_department_id=department_id,
            is_bookable=is_bookable,
            warranty_expiry_date=warranty_expiry_date,
            expected_retirement_date=expected_retirement_date,
            created_by=created_by,
        )
        db.add(asset)
        await db.flush()

        # Log initial status
        await asset_repo.add_status_history(
            db,
            asset_id=asset.id,
            previous_status=None,
            new_status="Available",
            changed_by=created_by,
            remarks="Asset registered",
            reference_type="Manual",
        )

        return asset

    async def update_asset(
        self,
        db: AsyncSession,
        *,
        asset_id: UUID,
        updated_by: UUID,
        **fields,
    ) -> Asset:
        asset = await asset_repo.get(db, asset_id)
        if not asset or asset.deleted_at:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")

        # Handle status transition
        new_status = fields.pop("current_status", None)
        if new_status and new_status != asset.current_status:
            old_status = asset.current_status
            asset.current_status = new_status
            asset.updated_at = datetime.now(timezone.utc)
            await asset_repo.add_status_history(
                db,
                asset_id=asset.id,
                previous_status=old_status,
                new_status=new_status,
                changed_by=updated_by,
                remarks=fields.pop("status_remarks", None),
                reference_type="Manual",
            )

        for key, val in fields.items():
            if val is not None and hasattr(asset, key):
                setattr(asset, key, val)

        asset.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return asset

    async def change_status(
        self,
        db: AsyncSession,
        asset: Asset,
        new_status: str,
        changed_by: Optional[UUID] = None,
        remarks: Optional[str] = None,
        reference_type: Optional[str] = "Manual",
        reference_id: Optional[UUID] = None,
    ) -> None:
        """Change an asset's lifecycle status and log it."""
        old_status = asset.current_status
        asset.current_status = new_status
        asset.updated_at = datetime.now(timezone.utc)
        await asset_repo.add_status_history(
            db,
            asset_id=asset.id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        await db.flush()

    async def soft_delete(self, db: AsyncSession, asset_id: UUID) -> None:
        asset = await asset_repo.get(db, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")
        asset.deleted_at = datetime.now(timezone.utc)
        await db.flush()


asset_service = AssetService()
