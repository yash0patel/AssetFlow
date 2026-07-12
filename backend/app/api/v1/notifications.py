from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.notification_repository import notification_repo
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    category: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    notifications, total, unread = await notification_repo.list_notifications(
        db, user_id=current_user.id, category=category, is_read=is_read, skip=skip, limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return NotificationListResponse(
        items=notifications,
        total=total, page=page, page_size=page_size, pages=pages, unread_count=unread,
    )


@router.post("/{id}/read")
async def mark_read(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin_nested():
        n = await notification_repo.mark_read(db, id, current_user.id)
    await db.commit()
    return {"detail": "Marked as read.", "id": id}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin_nested():
        count = await notification_repo.mark_all_read(db, current_user.id)
    await db.commit()
    return {"detail": f"Marked {count} notifications as read."}
