from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.profile import (
    AvatarOption,
    AvatarSelectionPayload,
    EmailVerificationConfirmPayload,
    EmailVerificationConfirmResponse,
    EmailVerificationSendResponse,
    EmailVerificationStatusResponse,
    NotificationSettings,
    NotificationSettingsUpdate,
    UserProfileResponse,
    UsernameUpdatePayload,
)
from app.schemas.user import UserPublic
from app.services.profile_service import (
    confirm_my_email_verification_code,
    get_avatar_options,
    get_email_verification_status,
    get_my_notification_settings,
    get_my_profile,
    send_my_email_verification_code,
    update_my_avatar,
    update_my_notification_settings,
    update_my_username,
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


@router.patch("/me/username", response_model=UserProfileResponse)
async def update_my_username_endpoint(
    payload: UsernameUpdatePayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await update_my_username(current_user.id, payload)


@router.get(
    "/me/email-verification/status",
    response_model=EmailVerificationStatusResponse,
)
async def read_my_email_verification_status(
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_email_verification_status(current_user.id)


@router.post(
    "/me/email-verification/send-code",
    response_model=EmailVerificationSendResponse,
)
async def send_my_email_verification_code_endpoint(
    current_user: UserPublic = Depends(get_current_user),
):
    return await send_my_email_verification_code(current_user.id)


@router.post(
    "/me/email-verification/confirm",
    response_model=EmailVerificationConfirmResponse,
)
async def confirm_my_email_verification_code_endpoint(
    payload: EmailVerificationConfirmPayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await confirm_my_email_verification_code(current_user.id, payload)



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