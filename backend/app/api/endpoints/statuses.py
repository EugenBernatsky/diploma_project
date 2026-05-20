from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.schemas.status import (
    ItemStatus,
    MediaItemWithStatus,
    StatusActionResponse,
    StatusPayload,
    UserItemStatusResponse,
)
from app.schemas.user import UserPublic
from app.services.statuses_service import (
    get_my_status,
    get_statuses,
    remove_status,
    set_status,
)

router = APIRouter(prefix="/statuses", tags=["statuses"])


@router.get("", response_model=list[MediaItemWithStatus])
async def read_statuses(
    status: ItemStatus | None = Query(default=None),
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_statuses(current_user.id, status)


@router.get("/{item_id}/me", response_model=UserItemStatusResponse)
async def read_my_status(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await get_my_status(current_user.id, item_id)


@router.put("/{item_id}", response_model=StatusActionResponse)
async def set_status_endpoint(
    item_id: str,
    payload: StatusPayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await set_status(current_user.id, item_id, payload)


@router.delete("/{item_id}", response_model=StatusActionResponse)
async def delete_status_endpoint(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await remove_status(current_user.id, item_id)