from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas.item import MediaItem, Category
from app.services.items_service import get_item_by_id, get_items

from app.schemas.item import MediaItem, Category, ItemStatsResponse
from app.services.items_service import get_item_by_id, get_item_stats, get_items

from app.schemas.item import MediaItem, Category, ItemStatsResponse, ItemsCountResponse
from app.services.items_service import get_item_by_id, get_item_stats, get_items, get_items_count

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[MediaItem])
async def read_items(
    category: Category | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    skip: int = Query(default=0, ge=0),
):
    return await get_items(category=category, limit=limit, skip=skip)

@router.get("/count", response_model=ItemsCountResponse)
async def read_items_count(category: Category | None = Query(default=None)):
    return await get_items_count(category=category)

@router.get("/{item_id}/stats", response_model=ItemStatsResponse)
async def read_item_stats(item_id: str):
    return await get_item_stats(item_id)

@router.get("/{item_id}", response_model=MediaItem)
async def read_item_by_id(item_id: str):
    item = await get_item_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item