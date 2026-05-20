from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_admin
from app.schemas.item import (
    Category,
    ItemActionResponse,
    MediaItem,
    MediaItemCreate,
    MediaItemUpdate,
)
from app.schemas.user import UserPublic
from app.services.admin_items_service import (
    create_item_admin,
    delete_item_admin,
    get_items_for_admin,
    update_item_admin,
)

router = APIRouter(prefix="/admin/items", tags=["admin-items"])


@router.get("", response_model=list[MediaItem])
async def read_items_for_admin(
    category: Category | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_items_for_admin(category=category, limit=limit)


@router.post("", response_model=MediaItem, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    payload: MediaItemCreate,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await create_item_admin(payload)


@router.put("/{item_id}", response_model=MediaItem)
async def update_item_endpoint(
    item_id: str,
    payload: MediaItemUpdate,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await update_item_admin(item_id, payload)


@router.delete("/{item_id}", response_model=ItemActionResponse)
async def delete_item_endpoint(
    item_id: str,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await delete_item_admin(item_id)