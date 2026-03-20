from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas import MediaItem
from app.services.items_service import get_mock_item_by_id, get_mock_items

router = APIRouter(prefix="/items", tags=["items"])

Category = Literal["movie", "series", "book"]


@router.get("", response_model=list[MediaItem])
def get_items(category: Category | None = Query(default=None)):
    return get_mock_items(category)


@router.get("/{item_id}", response_model=MediaItem)
def get_item_by_id(item_id: int):
    item = get_mock_item_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item