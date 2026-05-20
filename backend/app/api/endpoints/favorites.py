from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.schemas.favorite import FavoriteActionResponse
from app.schemas.item import MediaItem
from app.schemas.user import UserPublic
from app.services.favorites_service import (
    add_to_favorites,
    get_favorites,
    remove_from_favorites,
)

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[MediaItem])
async def read_favorites(current_user: UserPublic = Depends(get_current_user)):
    return await get_favorites(current_user.id)


@router.post("/{item_id}", response_model=FavoriteActionResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await add_to_favorites(current_user.id, item_id)


@router.delete("/{item_id}", response_model=FavoriteActionResponse)
async def delete_favorite_endpoint(item_id: str, current_user: UserPublic = Depends(get_current_user)):
    return await remove_from_favorites(current_user.id, item_id)