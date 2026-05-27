from __future__ import annotations

from bson import ObjectId

from app.db.mongo import get_db


async def find_recommendation_items(
    limit: int = 5000,
    category: str | None = None,
) -> list[dict]:
    db = get_db()

    query: dict = {}

    if category is not None:
        query["category"] = category

    return await db.media_items.find(query).to_list(length=limit)


async def find_user_recommendation_signals(user_id: str) -> dict:
    if not ObjectId.is_valid(user_id):
        return {
            "ratings": [],
            "favorites": [],
            "statuses": [],
            "interactions": [],
        }

    db = get_db()
    user_object_id = ObjectId(user_id)

    ratings = await db.ratings.find(
        {"user_id": user_object_id}
    ).to_list(length=1000)

    favorites = await db.favorites.find(
        {"user_id": user_object_id}
    ).to_list(length=1000)

    statuses = await db.item_statuses.find(
        {"user_id": user_object_id}
    ).to_list(length=1000)

    interactions = await db.interactions.find(
        {"user_id": user_object_id}
    ).sort("created_at", -1).to_list(length=300)

    return {
        "ratings": ratings,
        "favorites": favorites,
        "statuses": statuses,
        "interactions": interactions,
    }


async def find_items_by_string_ids(
    item_ids: list[str],
    category: str | None = None,
) -> list[dict]:
    valid_ids = [
        ObjectId(item_id)
        for item_id in item_ids
        if ObjectId.is_valid(item_id)
    ]

    if not valid_ids:
        return []

    query: dict = {
        "_id": {
            "$in": valid_ids,
        }
    }

    if category is not None:
        query["category"] = category

    db = get_db()

    return await db.media_items.find(query).to_list(length=len(valid_ids))


async def get_popularity_scores() -> dict[str, float]:
    db = get_db()
    scores: dict[str, float] = {}

    favorites_cursor = await db.favorites.aggregate(
        [
            {
                "$group": {
                    "_id": "$item_id",
                    "count": {"$sum": 1},
                }
            },
        ]
    )

    async for doc in favorites_cursor:
        if doc.get("_id") is None:
            continue

        item_id = str(doc["_id"])
        scores[item_id] = scores.get(item_id, 0.0) + float(doc.get("count", 0)) * 3.0

    ratings_cursor = await db.ratings.aggregate(
        [
            {
                "$group": {
                    "_id": "$item_id",
                    "count": {"$sum": 1},
                    "avg": {"$avg": "$score"},
                }
            },
        ]
    )

    async for doc in ratings_cursor:
        if doc.get("_id") is None:
            continue

        item_id = str(doc["_id"])
        count = float(doc.get("count", 0))
        avg = float(doc.get("avg", 0) or 0)

        # Average rating показує якість, count — впевненість.
        scores[item_id] = scores.get(item_id, 0.0) + avg * max(count, 1.0)

    interactions_cursor = await db.interactions.aggregate(
        [
            {
                "$group": {
                    "_id": "$item_id",
                    "count": {"$sum": 1},
                }
            },
        ]
    )

    async for doc in interactions_cursor:
        if doc.get("_id") is None:
            continue

        item_id = str(doc["_id"])
        scores[item_id] = scores.get(item_id, 0.0) + float(doc.get("count", 0)) * 0.5

    return scores


async def get_collaborative_data_stats() -> dict:
    db = get_db()

    users_count = await db.users.count_documents({})
    ratings_count = await db.ratings.count_documents({})

    return {
        "users_count": users_count,
        "ratings_count": ratings_count,
        "is_available": users_count >= 20 and ratings_count >= 100,
    }