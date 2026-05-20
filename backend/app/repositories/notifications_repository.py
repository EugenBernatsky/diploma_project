from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.notification import NotificationType


async def insert_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    created_at: datetime,
    item_id: str | None = None,
    comment_id: str | None = None,
    thread_id: str | None = None,
    post_id: str | None = None,
) -> dict:
    db = get_db()

    notification_data = {
        "user_id": ObjectId(user_id),
        "type": notification_type,
        "title": title,
        "message": message,
        "is_read": False,
        "item_id": ObjectId(item_id) if item_id and ObjectId.is_valid(item_id) else None,
        "comment_id": ObjectId(comment_id) if comment_id and ObjectId.is_valid(comment_id) else None,
        "thread_id": ObjectId(thread_id) if thread_id and ObjectId.is_valid(thread_id) else None,
        "post_id": ObjectId(post_id) if post_id and ObjectId.is_valid(post_id) else None,
        "created_at": created_at,
    }

    result = await db.notifications.insert_one(notification_data)
    created_notification = await db.notifications.find_one({"_id": result.inserted_id})

    if created_notification is None:
        raise RuntimeError("Failed to fetch created notification")

    return created_notification


async def find_notifications_by_user(
    user_id: str,
    unread_only: bool = False,
    limit: int = 100,
) -> list[dict]:
    if not ObjectId.is_valid(user_id):
        return []

    db = get_db()

    query: dict = {"user_id": ObjectId(user_id)}
    if unread_only:
        query["is_read"] = False

    return await db.notifications.find(query).sort("created_at", -1).to_list(length=limit)


async def count_unread_notifications_by_user(user_id: str) -> int:
    if not ObjectId.is_valid(user_id):
        return 0

    db = get_db()

    return await db.notifications.count_documents(
        {
            "user_id": ObjectId(user_id),
            "is_read": False,
        }
    )


async def mark_notification_as_read(user_id: str, notification_id: str) -> bool:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(notification_id):
        return False

    db = get_db()

    result = await db.notifications.update_one(
        {
            "_id": ObjectId(notification_id),
            "user_id": ObjectId(user_id),
        },
        {
            "$set": {
                "is_read": True,
            }
        },
    )

    return result.matched_count > 0


async def mark_all_notifications_as_read(user_id: str) -> int:
    if not ObjectId.is_valid(user_id):
        return 0

    db = get_db()

    result = await db.notifications.update_many(
        {
            "user_id": ObjectId(user_id),
            "is_read": False,
        },
        {
            "$set": {
                "is_read": True,
            }
        },
    )

    return result.modified_count


async def delete_notifications_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.notifications.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count