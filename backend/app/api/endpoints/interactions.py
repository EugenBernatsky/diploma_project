from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.interaction import (
    InteractionActionResponse,
    InteractionCreate,
    InteractionResponse,
    InteractionType,
)
from app.schemas.user import UserPublic
from app.services.interactions_service import create_interaction, get_my_interactions

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionActionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction_endpoint(
    payload: InteractionCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await create_interaction(current_user.id, payload)


@router.get("/me", response_model=list[InteractionResponse])
async def read_my_interactions(
    interaction_type: InteractionType | None = Query(default=None),
    item_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_my_interactions(
        user_id=current_user.id,
        interaction_type=interaction_type,
        item_id=item_id,
        limit=limit,
    )