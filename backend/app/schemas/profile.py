from datetime import datetime
from typing import Literal

from pydantic import BaseModel


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


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    avatar_id: str
    created_at: datetime
    notification_settings: NotificationSettings