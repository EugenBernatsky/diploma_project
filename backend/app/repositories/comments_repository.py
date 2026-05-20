from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db


async def find_comments_by_item(item_id: str, limit: int = 100) -> list[dict]:
    if not ObjectId.is_valid(item_id):
        return []

    db = get_db()

    return await db.comments.find(
        {"item_id": ObjectId(item_id)}
    ).sort("created_at", 1).to_list(length=limit)


async def find_recent_comments(limit: int = 100) -> list[dict]:
    db = get_db()

    return await db.comments.find({}).sort("created_at", -1).to_list(length=limit)


async def find_comment_by_id(comment_id: str) -> dict | None:
    if not ObjectId.is_valid(comment_id):
        return None

    db = get_db()
    return await db.comments.find_one({"_id": ObjectId(comment_id)})


async def insert_comment(
    user_id: str,
    item_id: str,
    author_username: str,
    author_avatar_id: str,
    text: str,
    parent_comment_id: str | None,
    created_at: datetime,
    updated_at: datetime,
) -> dict:
    db = get_db()

    comment_data = {
        "user_id": ObjectId(user_id),
        "item_id": ObjectId(item_id),
        "author_username": author_username,
        "author_avatar_id": author_avatar_id,
        "text": text,
        "parent_comment_id": ObjectId(parent_comment_id) if parent_comment_id else None,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    result = await db.comments.insert_one(comment_data)
    created_comment = await db.comments.find_one({"_id": result.inserted_id})

    if created_comment is None:
        raise RuntimeError("Failed to fetch created comment")

    return created_comment


async def update_comment_text(
    comment_id: str,
    text: str,
    updated_at: datetime,
) -> dict | None:
    if not ObjectId.is_valid(comment_id):
        return None

    db = get_db()

    await db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$set": {
                "text": text,
                "updated_at": updated_at,
            }
        },
    )

    return await db.comments.find_one({"_id": ObjectId(comment_id)})


async def delete_comment_tree(comment_id: str) -> bool:
    if not ObjectId.is_valid(comment_id):
        return False

    db = get_db()
    comment_object_id = ObjectId(comment_id)

    result = await db.comments.delete_many(
        {
            "$or": [
                {"_id": comment_object_id},
                {"parent_comment_id": comment_object_id},
            ]
        }
    )

    return result.deleted_count > 0


async def delete_comments_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.comments.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count