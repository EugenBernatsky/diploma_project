import re
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.profile_defaults import (
    AVATAR_OPTIONS,
    DEFAULT_AVATAR_ID,
    VALID_AVATAR_IDS,
    get_default_notification_settings,
)
from app.core.security import hash_verification_code, verify_verification_code
from app.repositories.users_repository import (
    find_user_by_id,
    find_user_by_username_except_user,
    update_user_fields,
)
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
from app.services.email_service import send_email_verification_code

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

def _to_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value.astimezone(UTC)

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
    username_updated_at = _to_utc_datetime(user_doc.get("username_updated_at"))

    username_can_be_changed_at = None
    if username_updated_at is not None:
        username_can_be_changed_at = username_updated_at + timedelta(
            days=settings.USERNAME_CHANGE_COOLDOWN_DAYS,
        )

    return UserProfileResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        role=user_doc["role"],
        avatar_id=_get_user_avatar_id(user_doc),
        created_at=user_doc["created_at"],
        notification_settings=_get_user_notification_settings(user_doc),
        email_verified=user_doc.get("email_verified", False),
        username_updated_at=username_updated_at,
        username_can_be_changed_at=username_can_be_changed_at,
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


async def update_my_username(
    user_id: str,
    payload: UsernameUpdatePayload,
) -> UserProfileResponse:
    new_username = payload.username.strip()

    if not USERNAME_PATTERN.fullmatch(new_username):
        raise HTTPException(
            status_code=400,
            detail="Username can contain only latin letters, numbers and underscores",
        )

    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_username = user_doc["username"]

    if new_username == current_username:
        raise HTTPException(
            status_code=400,
            detail="New username must be different from current username",
        )

    existing_user = await find_user_by_username_except_user(new_username, user_id)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already taken")

    now = datetime.now(UTC)

    username_updated_at = _to_utc_datetime(user_doc.get("username_updated_at"))

    if username_updated_at is not None:
        next_available_at = username_updated_at + timedelta(
            days=settings.USERNAME_CHANGE_COOLDOWN_DAYS,
        )

        if now < next_available_at:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Username can be changed only once every "
                    f"{settings.USERNAME_CHANGE_COOLDOWN_DAYS} days. "
                    f"Next available at: {next_available_at.isoformat()}"
                ),
            )

    updated_user = await update_user_fields(
        user_id,
        {
            "username": new_username,
            "username_updated_at": now,
            "updated_at": now,
        },
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _map_doc_to_profile_response(updated_user)


async def get_email_verification_status(
    user_id: str,
) -> EmailVerificationStatusResponse:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    return EmailVerificationStatusResponse(
        email=user_doc["email"],
        email_verified=user_doc.get("email_verified", False),
        email_verification_sent_at=_to_utc_datetime(
            user_doc.get("email_verification_sent_at")
        ),
        email_verification_expires_at=_to_utc_datetime(
            user_doc.get("email_verification_expires_at")
        ),
    )


async def send_my_email_verification_code(
    user_id: str,
) -> EmailVerificationSendResponse:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified",
        )

    now = datetime.now(UTC)

    sent_at = _to_utc_datetime(user_doc.get("email_verification_sent_at"))

    if sent_at is not None:
        seconds_since_last_send = (now - sent_at).total_seconds()

        if seconds_since_last_send < settings.EMAIL_VERIFICATION_RESEND_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Verification code was sent recently. "
                    f"Try again in {int(settings.EMAIL_VERIFICATION_RESEND_SECONDS - seconds_since_last_send)} seconds."
                ),
            )

    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = now + timedelta(
        minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES,
    )

    updated_user = await update_user_fields(
        user_id,
        {
            "email_verification_code_hash": hash_verification_code(code),
            "email_verification_expires_at": expires_at,
            "email_verification_sent_at": now,
            "email_verification_attempts": 0,
            "updated_at": now,
        },
    )

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        await send_email_verification_code(
            to_email=updated_user["email"],
            username=updated_user["username"],
            code=code,
        )
    except HTTPException:
        await update_user_fields(
            user_id,
            {
                "email_verification_code_hash": None,
                "email_verification_expires_at": None,
                "email_verification_attempts": 0,
                "updated_at": datetime.now(UTC),
            },
        )
        raise

    return EmailVerificationSendResponse(
        message="Verification code was sent to your email",
        expires_at=expires_at,
    )


async def confirm_my_email_verification_code(
    user_id: str,
    payload: EmailVerificationConfirmPayload,
) -> EmailVerificationConfirmResponse:
    user_doc = await find_user_by_id(user_id)

    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_doc.get("email_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified",
        )

    code_hash = user_doc.get("email_verification_code_hash")
    expires_at = _to_utc_datetime(user_doc.get("email_verification_expires_at"))
    attempts = int(user_doc.get("email_verification_attempts") or 0)

    if not code_hash or expires_at is None:
        raise HTTPException(
            status_code=400,
            detail="Verification code was not requested",
        )

    now = datetime.now(UTC)

    if now > expires_at:
        await update_user_fields(
            user_id,
            {
                "email_verification_code_hash": None,
                "email_verification_expires_at": None,
                "email_verification_attempts": 0,
                "updated_at": now,
            },
        )

        raise HTTPException(
            status_code=400,
            detail="Verification code expired. Request a new code.",
        )

    if attempts >= settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=400,
            detail="Too many incorrect attempts. Request a new code.",
        )

    is_valid_code = verify_verification_code(payload.code, code_hash)

    if not is_valid_code:
        await update_user_fields(
            user_id,
            {
                "email_verification_attempts": attempts + 1,
                "updated_at": now,
            },
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid verification code",
        )

    await update_user_fields(
        user_id,
        {
            "email_verified": True,
            "email_verification_code_hash": None,
            "email_verification_expires_at": None,
            "email_verification_sent_at": None,
            "email_verification_attempts": 0,
            "updated_at": now,
        },
    )

    return EmailVerificationConfirmResponse(
        message="Email verified successfully",
        email_verified=True,
    )