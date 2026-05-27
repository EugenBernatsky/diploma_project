from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.schemas.item import Category
from app.schemas.recommendation import RecommendationsResponse, SimilarItemsResponse
from app.schemas.user import UserPublic
from app.services.recommendations_service import (
    get_personal_recommendations,
    get_similar_items,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationsResponse)
async def read_my_recommendations(
    limit: int = Query(default=30, ge=1, le=50),
    category: Category | None = Query(default=None),
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_personal_recommendations(
        user_id=current_user.id,
        limit=limit,
        category=category,
    )


@router.get("/similar/{item_id}", response_model=SimilarItemsResponse)
async def read_similar_items(
    item_id: str,
    limit: int = Query(default=12, ge=1, le=30),
    category: Category | None = Query(default=None),
):
    return await get_similar_items(
        item_id=item_id,
        limit=limit,
        category=category,
    )