from fastapi import APIRouter, HTTPException, Query

from app.schemas.item import (
    Category,
    ItemSort,
    ItemStatsResponse,
    ItemsCountResponse,
    ItemsListResponse,
    MediaItem,
)
from app.services.items_service import (
    get_item_by_id,
    get_item_stats,
    get_items,
    get_items_count,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemsListResponse)
async def read_items(
    search: str | None = Query(default=None),
    category: Category | None = Query(default=None),
    genres: list[str] | None = Query(default=None),
    year_from: int | None = Query(default=None),
    year_to: int | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    runtime_from: int | None = Query(default=None),
    runtime_to: int | None = Query(default=None),
    sort: ItemSort = Query(default="relevance"),
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    return await get_items(
        search=search,
        category=category,
        genres=genres,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime_from=runtime_from,
        runtime_to=runtime_to,
        sort=sort,
        limit=limit,
        skip=skip,
    )

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
