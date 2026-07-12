from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.asset import Asset
from app.repositories.asset_repository import asset_repo
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.asset import (
    AssetCreate, AssetUpdate, AssetResponse, AssetDetailResponse,
    AssetListResponse, AssetLocationResponse, AssetStatusHistoryResponse,
)
from app.services.asset_service import asset_service

router = APIRouter()


async def require_asset_manager_or_admin(db: AsyncSession, user: User) -> None:
    role = await user_repo.get_user_role_name(db, user.id)
    if role not in ("admin", "asset_manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Asset Manager or Admin access required.")


def _build_response(asset: Asset) -> dict:
    holder_name = None
    if asset.current_holder_employee and asset.current_holder_employee.user:
        p = asset.current_holder_employee.user.profile
        if p:
            holder_name = f"{p.first_name} {p.last_name or ''}".strip()

    return {
        "id": asset.id,
        "asset_tag": asset.asset_tag,
        "name": asset.name,
        "category_id": asset.category_id,
        "category_name": asset.category.name if asset.category else None,
        "serial_number": asset.serial_number,
        "description": asset.description,
        "acquisition_date": asset.acquisition_date,
        "acquisition_cost": asset.acquisition_cost,
        "condition": asset.condition,
        "current_status": asset.current_status,
        "location_id": asset.current_location_id,
        "location_name": asset.current_location.name if asset.current_location else None,
        "department_id": asset.owning_department_id,
        "department_name": asset.owning_department.name if asset.owning_department else None,
        "is_bookable": asset.is_bookable,
        "warranty_expiry_date": asset.warranty_expiry_date,
        "expected_retirement_date": asset.expected_retirement_date,
        "current_holder_employee_id": asset.current_holder_employee_id,
        "current_holder_name": holder_name,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at,
    }


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    search: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    department_id: Optional[UUID] = Query(None),
    location_id: Optional[UUID] = Query(None),
    is_bookable: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    assets, total = await asset_repo.list_assets(
        db,
        search=search,
        category_id=category_id,
        status=status_filter,
        department_id=department_id,
        location_id=location_id,
        is_bookable=is_bookable,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return AssetListResponse(
        items=[_build_response(a) for a in assets],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def register_asset(
    payload: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_asset_manager_or_admin(db, current_user)

    async with db.begin_nested():
        asset = await asset_service.create_asset(
            db,
            name=payload.name,
            category_id=payload.category_id,
            serial_number=payload.serial_number,
            description=payload.description,
            acquisition_date=payload.acquisition_date,
            acquisition_cost=payload.acquisition_cost,
            condition=payload.condition,
            location_id=payload.location_id,
            department_id=payload.department_id,
            is_bookable=payload.is_bookable,
            warranty_expiry_date=payload.warranty_expiry_date,
            expected_retirement_date=payload.expected_retirement_date,
            created_by=current_user.id,
        )
    await db.commit()

    db_asset = await asset_repo.get_by_id_with_relations(db, asset.id)
    return _build_response(db_asset)


@router.get("/locations", response_model=List[AssetLocationResponse])
async def list_locations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    locations = await asset_repo.list_locations(db)
    return [{"id": l.id, "name": l.name, "location_type": l.location_type} for l in locations]


@router.get("/bookable", response_model=List[AssetResponse])
async def list_bookable_assets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all assets marked as bookable resources."""
    assets = await asset_repo.list_bookable_assets(db)
    return [_build_response(a) for a in assets]


@router.get("/{id}", response_model=AssetDetailResponse)
async def get_asset(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset = await asset_repo.get_by_id_with_relations(db, id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")

    history = await asset_repo.get_status_history(db, id)
    resp = _build_response(asset)
    resp["status_history"] = [
        {
            "id": h.id,
            "previous_status": h.previous_status,
            "new_status": h.new_status,
            "reference_type": h.reference_type,
            "remarks": h.remarks,
            "changed_at": h.changed_at,
        }
        for h in history
    ]
    return resp


@router.patch("/{id}", response_model=AssetResponse)
async def update_asset(
    id: UUID,
    payload: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_asset_manager_or_admin(db, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    async with db.begin_nested():
        asset = await asset_service.update_asset(
            db,
            asset_id=id,
            updated_by=current_user.id,
            current_status=update_data.pop("current_status", None),
            status_remarks=update_data.pop("status_remarks", None),
            **{
                k: v for k, v in update_data.items()
                if k not in ("location_id", "department_id")
            },
            current_location_id=update_data.get("location_id"),
            owning_department_id=update_data.get("department_id"),
        )
    await db.commit()

    db_asset = await asset_repo.get_by_id_with_relations(db, id)
    return _build_response(db_asset)
