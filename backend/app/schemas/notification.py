from datetime import datetime
from typing import Literal

from pydantic import BaseModel


NotificationType = Literal[
    "reply_to_comment",
    "comment_deleted_by_admin",
    "reply_to_forum_thread",
    "reply_to_forum_post",
    "forum_thread_deleted_by_admin",
    "forum_post_deleted_by_admin",
]


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    is_read: bool

    item_id: str | None = None
    comment_id: str | None = None

    thread_id: str | None = None
    post_id: str | None = None

    created_at: datetime


class NotificationActionResponse(BaseModel):
    message: str


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int