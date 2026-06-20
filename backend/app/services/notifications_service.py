from datetime import UTC, datetime

from fastapi import HTTPException

from app.core.profile_defaults import get_default_notification_settings
from app.repositories.notifications_repository import (
    count_unread_notifications_by_user,
    find_notifications_by_user,
    insert_notification,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)
from app.repositories.users_repository import find_user_by_id
from app.schemas.notification import (
    NotificationActionResponse,
    NotificationResponse,
    NotificationType,
    NotificationUnreadCountResponse,
)


NOTIFICATION_TYPE_TO_SETTING_KEY = {
    "reply_to_comment": "comment_replies",
    "comment_deleted_by_admin": "comment_admin_actions",
    "reply_to_forum_thread": "forum_thread_replies",
    "reply_to_forum_post": "forum_post_replies",
    "forum_thread_deleted_by_admin": "forum_admin_actions",
    "forum_post_deleted_by_admin": "forum_admin_actions",
}


def _map_doc_to_notification_response(doc: dict) -> NotificationResponse:
    item_id = doc.get("item_id")
    comment_id = doc.get("comment_id")
    thread_id = doc.get("thread_id")
    post_id = doc.get("post_id")

    return NotificationResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        type=doc["type"],
        title=doc["title"],
        message=doc["message"],
        is_read=doc["is_read"],
        item_id=str(item_id) if item_id is not None else None,
        comment_id=str(comment_id) if comment_id is not None else None,
        thread_id=str(thread_id) if thread_id is not None else None,
        post_id=str(post_id) if post_id is not None else None,
        created_at=doc["created_at"],
    )


async def _is_notification_enabled_for_user(
    user_id: str,
    notification_type: NotificationType,
) -> bool:
    setting_key = NOTIFICATION_TYPE_TO_SETTING_KEY.get(notification_type)
    if setting_key is None:
        return True

    user_doc = await find_user_by_id(user_id)
    if user_doc is None:
        return False

    default_settings = get_default_notification_settings()
    user_settings = user_doc.get("notification_settings") or {}
    merged = {
        **default_settings,
        **user_settings,
    }

    return bool(merged.get(setting_key, True))


async def create_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    item_id: str | None = None,
    comment_id: str | None = None,
    thread_id: str | None = None,
    post_id: str | None = None,
) -> NotificationResponse | None:
    is_enabled = await _is_notification_enabled_for_user(user_id, notification_type)
    if not is_enabled:
        return None

    created = await insert_notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        item_id=item_id,
        comment_id=comment_id,
        thread_id=thread_id,
        post_id=post_id,
        created_at=datetime.now(UTC),
    )

    return _map_doc_to_notification_response(created)


async def notify_reply_to_comment(
    recipient_user_id: str,
    replier_username: str,
    item_id: str,
    item_title: str,
    reply_comment_id: str,
) -> None:
    await create_notification(
        user_id=recipient_user_id,
        notification_type="reply_to_comment",
        title="New reply to your comment",
        message=f"{replier_username} replied to your comment on '{item_title}'",
        item_id=item_id,
        comment_id=reply_comment_id,
    )


async def notify_comment_deleted_by_admin(
    recipient_user_id: str,
    item_id: str,
    item_title: str | None,
    deleted_comment_id: str,
) -> None:
    title_suffix = f" on '{item_title}'" if item_title else ""

    await create_notification(
        user_id=recipient_user_id,
        notification_type="comment_deleted_by_admin",
        title="Your comment was deleted",
        message=f"An administrator deleted your comment{title_suffix}",
        item_id=item_id,
        comment_id=deleted_comment_id,
    )


async def notify_reply_to_forum_thread(
    recipient_user_id: str,
    replier_username: str,
    thread_id: str,
    thread_title: str,
    post_id: str,
) -> None:
    await create_notification(
        user_id=recipient_user_id,
        notification_type="reply_to_forum_thread",
        title="New reply in your thread",
        message=f"{replier_username} wrote a new post in your thread '{thread_title}'",
        thread_id=thread_id,
        post_id=post_id,
    )


async def notify_reply_to_forum_post(
    recipient_user_id: str,
    replier_username: str,
    thread_id: str,
    thread_title: str,
    post_id: str,
) -> None:
    await create_notification(
        user_id=recipient_user_id,
        notification_type="reply_to_forum_post",
        title="New reply to your post",
        message=f"{replier_username} replied to your post in '{thread_title}'",
        thread_id=thread_id,
        post_id=post_id,
    )


async def notify_forum_thread_deleted_by_admin(
    recipient_user_id: str,
    thread_id: str,
    thread_title: str,
) -> None:
    await create_notification(
        user_id=recipient_user_id,
        notification_type="forum_thread_deleted_by_admin",
        title="Your thread was deleted",
        message=f"An administrator deleted your thread '{thread_title}'",
        thread_id=thread_id,
    )


async def notify_forum_post_deleted_by_admin(
    recipient_user_id: str,
    thread_id: str,
    thread_title: str,
    post_id: str | None = None,
    reason: str | None = None,
) -> None:
    reason_suffix = f" {reason}" if reason else ""

    await create_notification(
        user_id=recipient_user_id,
        notification_type="forum_post_deleted_by_admin",
        title="Your post was deleted",
        message=f"An administrator deleted your post in '{thread_title}'.{reason_suffix}".strip(),
        thread_id=thread_id,
        post_id=post_id,
    )


async def get_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 100,
) -> list[NotificationResponse]:
    docs = await find_notifications_by_user(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit,
    )
    return [_map_doc_to_notification_response(doc) for doc in docs]


async def get_unread_notifications_count(user_id: str) -> NotificationUnreadCountResponse:
    unread_count = await count_unread_notifications_by_user(user_id)
    return NotificationUnreadCountResponse(unread_count=unread_count)


async def read_notification(user_id: str, notification_id: str) -> NotificationActionResponse:
    updated = await mark_notification_as_read(user_id, notification_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationActionResponse(message="Notification marked as read")


async def read_all_notifications(user_id: str) -> NotificationActionResponse:
    await mark_all_notifications_as_read(user_id)
    return NotificationActionResponse(message="All notifications marked as read")
