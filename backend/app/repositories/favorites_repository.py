from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db


async def find_favorite(user_id: str, item_id: str) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    return await db.favorites.find_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )


async def insert_favorite(user_id: str, item_id: str, created_at: datetime) -> dict:
    db = get_db()

    favorite_data = {
        "user_id": ObjectId(user_id),
        "item_id": ObjectId(item_id),
        "created_at": created_at,
    }

    result = await db.favorites.insert_one(favorite_data)
    created_favorite = await db.favorites.find_one({"_id": result.inserted_id})

    if created_favorite is None:
        raise RuntimeError("Failed to fetch created favorite")

    return created_favorite


async def delete_favorite(user_id: str, item_id: str) -> bool:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return False

    db = get_db()

    result = await db.favorites.delete_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )

    return result.deleted_count > 0


async def find_favorite_item_ids_by_user(user_id: str) -> list[str]:
    if not ObjectId.is_valid(user_id):
        return []

    db = get_db()

    docs = await db.favorites.find({"user_id": ObjectId(user_id)}).to_list(length=1000)

    return [str(doc["item_id"]) for doc in docs]


async def delete_favorites_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.favorites.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count