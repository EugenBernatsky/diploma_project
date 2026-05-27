from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.interaction import InteractionSource, InteractionType


async def insert_interaction(
    user_id: str,
    item_id: str,
    interaction_type: InteractionType,
    source: InteractionSource,
    created_at: datetime,
) -> dict:
    db = get_db()

    interaction_data = {
        "user_id": ObjectId(user_id),
        "item_id": ObjectId(item_id),
        "interaction_type": interaction_type,
        "source": source,
        "created_at": created_at,
    }

    result = await db.interactions.insert_one(interaction_data)
    created_interaction = await db.interactions.find_one({"_id": result.inserted_id})

    if created_interaction is None:
        raise RuntimeError("Failed to fetch created interaction")

    return created_interaction


async def find_interactions_by_user(
    user_id: str,
    interaction_type: InteractionType | None = None,
    item_id: str | None = None,
    limit: int = 100,
) -> list[dict]:
    if not ObjectId.is_valid(user_id):
        return []

    db = get_db()

    query: dict = {"user_id": ObjectId(user_id)}

    if interaction_type is not None:
        query["interaction_type"] = interaction_type

    if item_id is not None and ObjectId.is_valid(item_id):
        query["item_id"] = ObjectId(item_id)

    return await db.interactions.find(query).sort("created_at", -1).to_list(length=limit)


async def delete_interactions_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.interactions.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count