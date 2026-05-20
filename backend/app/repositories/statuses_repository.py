from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.status import ItemStatus


async def find_status(user_id: str, item_id: str) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    return await db.item_statuses.find_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )


async def upsert_status(
    user_id: str,
    item_id: str,
    status: ItemStatus,
    now: datetime,
) -> dict:
    db = get_db()

    await db.item_statuses.update_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        },
        {
            "$set": {
                "status": status,
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )

    saved_status = await db.item_statuses.find_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )

    if saved_status is None:
        raise RuntimeError("Failed to fetch saved status")

    return saved_status


async def delete_status(user_id: str, item_id: str) -> bool:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return False

    db = get_db()

    result = await db.item_statuses.delete_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )

    return result.deleted_count > 0


async def find_status_docs_by_user(
    user_id: str,
    status: ItemStatus | None = None,
) -> list[dict]:
    if not ObjectId.is_valid(user_id):
        return []

    db = get_db()

    query = {"user_id": ObjectId(user_id)}
    if status is not None:
        query["status"] = status

    return await db.item_statuses.find(query).sort("updated_at", -1).to_list(length=1000)


async def delete_statuses_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.item_statuses.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count