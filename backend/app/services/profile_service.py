from datetime import UTC, datetime

from fastapi import HTTPException

from app.core.profile_defaults import (
    AVATAR_OPTIONS,
    DEFAULT_AVATAR_ID,
    VALID_AVATAR_IDS,
    get_default_notification_settings,
)
from app.repositories.users_repository import find_user_by_id, update_user_fields
from app.schemas.profile import (
    AvatarOption,
    AvatarSelectionPayload,
    NotificationSettings,
    NotificationSettingsUpdate,
    UserProfileResponse,
)


def _get_user_avatar_id(user_doc: dict) -> str:
    avatar_id = user_doc.get("avatar_id")
    if avatar_id in VALID_AVATAR_IDS:
        return avatar_id
    return DEFAULT_AVATAR_ID


def _get_user_notification_settings(user_doc: dict) -> NotificationSettings:
    default_settings = get_default_notification_settings()
    user_settings = user_doc.get("notification_settings") or {}

    merged = {
        **default_settings,
        **user_settings,
    }

    return NotificationSettings(**merged)


def _map_doc_to_profile_response(user_doc: dict) -> UserProfileResponse:
    return UserProfileResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        role=user_doc["role"],
        avatar_id=_get_user_avatar_id(user_doc),
        created_at=user_doc["created_at"],
        notification_settings=_get_user_notification_settings(user_doc),
    )


async def get_my_profile(user_id: str) -> UserProfileResponse:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _map_doc_to_profile_response(user_doc)


async def get_avatar_options() -> list[AvatarOption]:
    return [AvatarOption(**avatar) for avatar in AVATAR_OPTIONS]


async def update_my_avatar(user_id: str, payload: AvatarSelectionPayload) -> UserProfileResponse:
    if payload.avatar_id not in VALID_AVATAR_IDS:
        raise HTTPException(status_code=400, detail="Invalid avatar_id")

    updated_user = await update_user_fields(
        user_id,
        {
            "avatar_id": payload.avatar_id,
            "updated_at": datetime.now(UTC),
        },
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _map_doc_to_profile_response(updated_user)


async def get_my_notification_settings(user_id: str) -> NotificationSettings:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _get_user_notification_settings(user_doc)


async def update_my_notification_settings(
    user_id: str,
    payload: NotificationSettingsUpdate,
) -> NotificationSettings:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_settings = _get_user_notification_settings(user_doc).model_dump()

    update_data = payload.model_dump(exclude_none=True)
    merged_settings = {
        **current_settings,
        **update_data,
    }

    updated_user = await update_user_fields(
        user_id,
        {
            "notification_settings": merged_settings,
            "updated_at": datetime.now(UTC),
        },
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _get_user_notification_settings(updated_user)