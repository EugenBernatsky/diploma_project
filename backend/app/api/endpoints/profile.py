from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.profile import (
    AvatarOption,
    AvatarSelectionPayload,
    NotificationSettings,
    NotificationSettingsUpdate,
    UserProfileResponse,
)
from app.schemas.user import UserPublic
from app.services.profile_service import (
    get_avatar_options,
    get_my_notification_settings,
    get_my_profile,
    update_my_avatar,
    update_my_notification_settings,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
async def read_my_profile(current_user: UserPublic = Depends(get_current_user)):
    return await get_my_profile(current_user.id)


@router.get("/avatar-options", response_model=list[AvatarOption])
async def read_avatar_options():
    return await get_avatar_options()


@router.patch("/me/avatar", response_model=UserProfileResponse)
async def update_my_avatar_endpoint(
    payload: AvatarSelectionPayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await update_my_avatar(current_user.id, payload)


@router.get("/me/notification-settings", response_model=NotificationSettings)
async def read_my_notification_settings(
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_my_notification_settings(current_user.id)


@router.patch("/me/notification-settings", response_model=NotificationSettings)
async def update_my_notification_settings_endpoint(
    payload: NotificationSettingsUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await update_my_notification_settings(current_user.id, payload)