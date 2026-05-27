from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db


async def find_posts_by_thread(thread_id: str, limit: int = 200) -> list[dict]:
    if not ObjectId.is_valid(thread_id):
        return []

    db = get_db()

    return await db.forum_posts.find(
        {"thread_id": ObjectId(thread_id)}
    ).sort("created_at", 1).to_list(length=limit)


async def find_recent_posts(limit: int = 100) -> list[dict]:
    db = get_db()

    return await db.forum_posts.find({}).sort("created_at", -1).to_list(length=limit)


async def find_post_by_id(post_id: str) -> dict | None:
    if not ObjectId.is_valid(post_id):
        return None

    db = get_db()
    return await db.forum_posts.find_one({"_id": ObjectId(post_id)})


async def find_post_tree_ids(post_id: str) -> list[str]:
    if not ObjectId.is_valid(post_id):
        return []

    db = get_db()
    post_object_id = ObjectId(post_id)

    docs = await db.forum_posts.find(
        {
            "$or": [
                {"_id": post_object_id},
                {"parent_post_id": post_object_id},
            ]
        },
        {"_id": 1},
    ).to_list(length=1000)

    return [str(doc["_id"]) for doc in docs]


async def find_post_tree_docs(post_id: str) -> list[dict]:
    if not ObjectId.is_valid(post_id):
        return []

    db = get_db()
    post_object_id = ObjectId(post_id)

    return await db.forum_posts.find(
        {
            "$or": [
                {"_id": post_object_id},
                {"parent_post_id": post_object_id},
            ]
        }
    ).to_list(length=1000)


async def find_post_ids_by_thread(thread_id: str) -> list[str]:
    if not ObjectId.is_valid(thread_id):
        return []

    db = get_db()

    docs = await db.forum_posts.find(
        {"thread_id": ObjectId(thread_id)},
        {"_id": 1},
    ).to_list(length=5000)

    return [str(doc["_id"]) for doc in docs]


async def insert_post(
    user_id: str,
    thread_id: str,
    author_username: str,
    author_avatar_id: str,
    text: str,
    parent_post_id: str | None,
    reply_to_post_id: str | None,
    reply_to_user_id: str | None,
    reply_to_username: str | None,
    created_at: datetime,
    updated_at: datetime,
) -> dict:
    db = get_db()

    post_data = {
        "user_id": ObjectId(user_id),
        "thread_id": ObjectId(thread_id),
        "author_username": author_username,
        "author_avatar_id": author_avatar_id,
        "text": text,
        "score": 0,

        # Для групування в один рівень вкладеності.
        "parent_post_id": ObjectId(parent_post_id) if parent_post_id else None,

        # Для точного адресата відповіді.
        "reply_to_post_id": ObjectId(reply_to_post_id) if reply_to_post_id else None,
        "reply_to_user_id": ObjectId(reply_to_user_id) if reply_to_user_id else None,
        "reply_to_username": reply_to_username,

        "created_at": created_at,
        "updated_at": updated_at,
    }

    result = await db.forum_posts.insert_one(post_data)
    created_post = await db.forum_posts.find_one({"_id": result.inserted_id})

    if created_post is None:
        raise RuntimeError("Failed to fetch created post")

    return created_post


async def update_post_text(
    post_id: str,
    text: str,
    updated_at: datetime,
) -> dict | None:
    if not ObjectId.is_valid(post_id):
        return None

    db = get_db()

    await db.forum_posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                "text": text,
                "updated_at": updated_at,
            }
        },
    )

    return await db.forum_posts.find_one({"_id": ObjectId(post_id)})


async def delete_post_tree(post_id: str) -> int:
    if not ObjectId.is_valid(post_id):
        return 0

    db = get_db()
    post_object_id = ObjectId(post_id)

    result = await db.forum_posts.delete_many(
        {
            "$or": [
                {"_id": post_object_id},
                {"parent_post_id": post_object_id},
            ]
        }
    )

    return result.deleted_count
        

async def delete_posts_by_thread_id(thread_id: str) -> int:
    if not ObjectId.is_valid(thread_id):
        return 0

    db = get_db()

    result = await db.forum_posts.delete_many({"thread_id": ObjectId(thread_id)})
    return result.deleted_count


async def increment_post_score(post_id: str, delta: int) -> None:
    if not ObjectId.is_valid(post_id) or delta == 0:
        return

    db = get_db()

    await db.forum_posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$inc": {"score": delta},
        },
    )