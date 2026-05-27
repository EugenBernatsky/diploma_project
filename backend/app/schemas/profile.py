from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


UserRole = Literal["user", "admin"]


class AvatarOption(BaseModel):
    id: str
    label: str
    image_url: str


class AvatarSelectionPayload(BaseModel):
    avatar_id: str


class NotificationSettings(BaseModel):
    comment_replies: bool
    comment_admin_actions: bool
    forum_thread_replies: bool
    forum_post_replies: bool
    forum_admin_actions: bool


class NotificationSettingsUpdate(BaseModel):
    comment_replies: bool | None = None
    comment_admin_actions: bool | None = None
    forum_thread_replies: bool | None = None
    forum_post_replies: bool | None = None
    forum_admin_actions: bool | None = None


class UsernameUpdatePayload(BaseModel):
    username: str = Field(min_length=3, max_length=50)


class EmailVerificationConfirmPayload(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class EmailVerificationSendResponse(BaseModel):
    message: str
    expires_at: datetime


class EmailVerificationConfirmResponse(BaseModel):
    message: str
    email_verified: bool


class EmailVerificationStatusResponse(BaseModel):
    email: str
    email_verified: bool
    email_verification_sent_at: datetime | None = None
    email_verification_expires_at: datetime | None = None


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    avatar_id: str
    created_at: datetime
    notification_settings: NotificationSettings

    email_verified: bool = False
    username_updated_at: datetime | None = None
    username_can_be_changed_at: datetime | None = None