from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db


async def find_rating(user_id: str, item_id: str) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    return await db.ratings.find_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )


async def insert_rating(user_id: str, item_id: str, score: int, created_at: datetime, updated_at: datetime) -> dict:
    db = get_db()

    rating_data = {
        "user_id": ObjectId(user_id),
        "item_id": ObjectId(item_id),
        "score": score,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    result = await db.ratings.insert_one(rating_data)
    created_rating = await db.ratings.find_one({"_id": result.inserted_id})

    if created_rating is None:
        raise RuntimeError("Failed to fetch created rating")

    return created_rating


async def update_rating(user_id: str, item_id: str, score: int, updated_at: datetime) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    await db.ratings.update_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        },
        {
            "$set": {
                "score": score,
                "updated_at": updated_at,
            }
        },
    )

    return await db.ratings.find_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )


async def delete_rating(user_id: str, item_id: str) -> bool:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(item_id):
        return False

    db = get_db()

    result = await db.ratings.delete_one(
        {
            "user_id": ObjectId(user_id),
            "item_id": ObjectId(item_id),
        }
    )

    return result.deleted_count > 0


async def delete_ratings_by_item_id(item_id: str) -> int:
    if not ObjectId.is_valid(item_id):
        return 0

    db = get_db()

    result = await db.ratings.delete_many({"item_id": ObjectId(item_id)})
    return result.deleted_count

async def get_rating_stats_by_item_id(item_id: str) -> dict:
    if not ObjectId.is_valid(item_id):
        return {
            "average": None,
            "count": 0,
        }

    db = get_db()

    cursor = await db.ratings.aggregate(
        [
            {
                "$match": {
                    "item_id": ObjectId(item_id),
                }
            },
            {
                "$group": {
                    "_id": "$item_id",
                    "average": {"$avg": "$score"},
                    "count": {"$sum": 1},
                }
            },
        ]
    )

    docs = await cursor.to_list(length=1)

    if not docs:
        return {
            "average": None,
            "count": 0,
        }

    return {
        "average": round(float(docs[0]["average"]), 2),
        "count": int(docs[0]["count"]),
    }