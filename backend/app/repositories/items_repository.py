from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.item import Category


async def find_items(category: Category | None = None, limit: int = 100) -> list[dict]:
    db = get_db()

    query = {}
    if category is not None:
        query["category"] = category

    return await db.media_items.find(query).to_list(length=limit)


async def find_item_by_id(item_id: str) -> dict | None:
    if not ObjectId.is_valid(item_id):
        return None

    db = get_db()
    return await db.media_items.find_one({"_id": ObjectId(item_id)})


async def find_items_by_ids(item_ids: list[str]) -> list[dict]:
    valid_object_ids = [ObjectId(item_id) for item_id in item_ids if ObjectId.is_valid(item_id)]

    if not valid_object_ids:
        return []

    db = get_db()
    return await db.media_items.find({"_id": {"$in": valid_object_ids}}).to_list(length=len(valid_object_ids))


async def insert_item(item_data: dict) -> dict:
    db = get_db()

    result = await db.media_items.insert_one(item_data)
    created_item = await db.media_items.find_one({"_id": result.inserted_id})

    if created_item is None:
        raise RuntimeError("Failed to fetch created item")

    return created_item


async def update_item_by_id(item_id: str, item_data: dict) -> dict | None:
    if not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    await db.media_items.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item_data},
    )

    return await db.media_items.find_one({"_id": ObjectId(item_id)})


async def delete_item_by_id(item_id: str) -> bool:
    if not ObjectId.is_valid(item_id):
        return False

    db = get_db()

    result = await db.media_items.delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count > 0