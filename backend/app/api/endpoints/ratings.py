from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.schemas.rating import RatingActionResponse, RatingPayload, UserRatingResponse
from app.schemas.user import UserPublic
from app.services.ratings_service import (
    create_rating,
    edit_rating,
    get_my_rating,
    remove_rating,
)

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.get("/{item_id}/me", response_model=UserRatingResponse)
async def read_my_rating(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await get_my_rating(current_user.id, item_id)


@router.post("/{item_id}", response_model=RatingActionResponse, status_code=status.HTTP_201_CREATED)
async def create_rating_endpoint(
    item_id: str,
    payload: RatingPayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await create_rating(current_user.id, item_id, payload)


@router.put("/{item_id}", response_model=RatingActionResponse)
async def update_rating_endpoint(
    item_id: str,
    payload: RatingPayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await edit_rating(current_user.id, item_id, payload)


@router.delete("/{item_id}", response_model=RatingActionResponse)
async def delete_rating_endpoint(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await remove_rating(current_user.id, item_id)