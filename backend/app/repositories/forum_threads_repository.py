from datetime import datetime

from bson import ObjectId
from pymongo import DESCENDING

from app.db.mongo import get_db


async def find_threads(
    limit: int = 100,
    sort_by: str = "activity",
    category_type: str | None = None,
    custom_category: str | None = None,
) -> list[dict]:
    db = get_db()

    filters: dict = {}

    if category_type:
        filters["category_type"] = category_type

    if custom_category:
        filters["custom_category"] = custom_category

    if sort_by == "score":
        cursor = db.forum_threads.find(filters).sort(
            [("score", DESCENDING), ("last_activity_at", DESCENDING)]
        )
    elif sort_by == "newest":
        cursor = db.forum_threads.find(filters).sort("created_at", DESCENDING)
    else:
        cursor = db.forum_threads.find(filters).sort("last_activity_at", DESCENDING)

    return await cursor.to_list(length=limit)


async def find_thread_by_id(thread_id: str) -> dict | None:
    if not ObjectId.is_valid(thread_id):
        return None

    db = get_db()
    return await db.forum_threads.find_one({"_id": ObjectId(thread_id)})


async def insert_thread(
    user_id: str,
    author_username: str,
    author_avatar_id: str,
    title: str,
    text: str,
    category_type: str,
    custom_category: str | None,
    created_at: datetime,
    updated_at: datetime,
    last_activity_at: datetime,
) -> dict:
    db = get_db()

    thread_data = {
        "user_id": ObjectId(user_id),
        "author_username": author_username,
        "author_avatar_id": author_avatar_id,
        "title": title,
        "text": text,
        "category_type": category_type,
        "custom_category": custom_category,
        "score": 0,
        "replies_count": 0,
        "created_at": created_at,
        "updated_at": updated_at,
        "last_activity_at": last_activity_at,
    }

    result = await db.forum_threads.insert_one(thread_data)
    created_thread = await db.forum_threads.find_one({"_id": result.inserted_id})

    if created_thread is None:
        raise RuntimeError("Failed to fetch created thread")

    return created_thread


async def update_thread_content(
    thread_id: str,
    title: str,
    text: str,
    category_type: str,
    custom_category: str | None,
    updated_at: datetime,
) -> dict | None:
    if not ObjectId.is_valid(thread_id):
        return None

    db = get_db()

    await db.forum_threads.update_one(
        {"_id": ObjectId(thread_id)},
        {
            "$set": {
                "title": title,
                "text": text,
                "category_type": category_type,
                "custom_category": custom_category,
                "updated_at": updated_at,
            }
        },
    )

    return await db.forum_threads.find_one({"_id": ObjectId(thread_id)})


async def delete_thread_by_id(thread_id: str) -> bool:
    if not ObjectId.is_valid(thread_id):
        return False

    db = get_db()

    result = await db.forum_threads.delete_one({"_id": ObjectId(thread_id)})
    return result.deleted_count > 0


async def increment_thread_replies_count(
    thread_id: str,
    last_activity_at: datetime,
) -> None:
    if not ObjectId.is_valid(thread_id):
        return

    db = get_db()

    await db.forum_threads.update_one(
        {"_id": ObjectId(thread_id)},
        {
            "$inc": {"replies_count": 1},
            "$set": {"last_activity_at": last_activity_at},
        },
    )


async def decrement_thread_replies_count(thread_id: str, amount: int = 1) -> None:
    if not ObjectId.is_valid(thread_id) or amount <= 0:
        return

    db = get_db()

    await db.forum_threads.update_one(
        {"_id": ObjectId(thread_id)},
        {
            "$inc": {"replies_count": -amount},
        },
    )


async def increment_thread_score(thread_id: str, delta: int) -> None:
    if not ObjectId.is_valid(thread_id) or delta == 0:
        return

    db = get_db()

    await db.forum_threads.update_one(
        {"_id": ObjectId(thread_id)},
        {
            "$inc": {"score": delta},
        },
    )