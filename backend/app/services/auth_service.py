import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.repositories.users_repository import find_user_by_id, find_user_by_username
from app.services.users_service import map_doc_to_user_public
from app.schemas.user import UserPublic


async def authenticate_user(username: str, password: str) -> str | None:
    user = await find_user_by_username(username)
    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    if not user["is_active"]:
        return None

    return str(user["_id"])


async def login_user(username: str, password: str) -> str | None:
    user_id = await authenticate_user(username, password)
    if user_id is None:
        return None

    return create_access_token(subject=user_id)


async def get_user_from_token(token: str) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user_doc = await find_user_by_id(user_id)
    if user_doc is None:
        raise credentials_exception

    if not user_doc["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")

    return map_doc_to_user_public(user_doc)