from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.activity_log_repository import activity_log_repo

router = APIRouter()


@router.get("/")
async def list_activity_logs(
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    logs, total = await activity_log_repo.list_logs(
        db,
        entity_type=entity_type,
        action=action,
        skip=skip,
        limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0

    items = []
    for log in logs:
        actor_name = None
        if log.actor_user:
            if log.actor_user.profile:
                p = log.actor_user.profile
                actor_name = f"{p.first_name} {p.last_name or ''}".strip()
            actor_name = actor_name or log.actor_user.email
        items.append({
            "id": log.id,
            "actor": actor_name or "System",
            "actor_role": log.actor_role,
            "action": log.action,
            "module_name": log.module_name,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "new_value": log.new_value,
            "created_at": log.created_at,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}
