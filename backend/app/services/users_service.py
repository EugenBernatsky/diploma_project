from datetime import UTC, datetime

from fastapi import HTTPException

from app.core.profile_defaults import (
    DEFAULT_AVATAR_ID,
    get_default_notification_settings,
)
from app.core.security import hash_password
from app.repositories.users_repository import (
    find_user_by_email,
    find_user_by_username,
    insert_user,
)
from app.schemas.user import UserCreate, UserPublic, UserRole


def map_doc_to_user_public(doc: dict) -> UserPublic:
    return UserPublic(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        role=doc["role"],
        is_active=doc["is_active"],
        created_at=doc["created_at"],
    )


async def create_user(user: UserCreate, role: UserRole = "user") -> UserPublic:
    existing_user_by_email = await find_user_by_email(user.email)
    if existing_user_by_email is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_user_by_username = await find_user_by_username(user.username)
    if existing_user_by_username is not None:
        raise HTTPException(status_code=400, detail="Username already taken")

    now = datetime.now(UTC)

    user_data = {
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "role": role,
        "is_active": True,
        "avatar_id": DEFAULT_AVATAR_ID,
        "notification_settings": get_default_notification_settings(),
        "created_at": now,
        "updated_at": now,
    }

    created_user = await insert_user(user_data)
    return map_doc_to_user_public(created_user)