from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas.item import MediaItem, Category
from app.services.items_service import get_item_by_id, get_items

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[MediaItem])
async def read_items(category: Category | None = Query(default=None)):
    return await get_items(category)


@router.get("/{item_id}", response_model=MediaItem)
async def read_item_by_id(item_id: str):
    item = await get_item_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item