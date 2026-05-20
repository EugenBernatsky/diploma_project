from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.user import UserPublic
from app.services.auth_service import get_user_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    return await get_user_from_token(token)


async def get_current_admin(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user