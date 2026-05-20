from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.user import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: UserPublic = Depends(get_current_user)):
    return current_user