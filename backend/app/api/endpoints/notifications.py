from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.schemas.notification import (
    NotificationActionResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.schemas.user import UserPublic
from app.services.notifications_service import (
    get_notifications,
    get_unread_notifications_count,
    read_all_notifications,
    read_notification,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def read_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
async def read_unread_notifications_count(
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_unread_notifications_count(current_user.id)


@router.patch("/{notification_id}/read", response_model=NotificationActionResponse)
async def mark_notification_as_read_endpoint(
    notification_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await read_notification(current_user.id, notification_id)


@router.patch("/read-all", response_model=NotificationActionResponse)
async def mark_all_notifications_as_read_endpoint(
    current_user: UserPublic = Depends(get_current_user),
):
    return await read_all_notifications(current_user.id)