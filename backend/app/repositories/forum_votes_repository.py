from datetime import datetime

from bson import ObjectId

from app.db.mongo import get_db
from app.schemas.forum_vote import ForumVoteTargetType, ForumVoteValue


async def find_vote(
    user_id: str,
    target_type: ForumVoteTargetType,
    target_id: str,
) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(target_id):
        return None

    db = get_db()

    return await db.forum_votes.find_one(
        {
            "user_id": ObjectId(user_id),
            "target_type": target_type,
            "target_id": ObjectId(target_id),
        }
    )


async def insert_vote(
    user_id: str,
    target_type: ForumVoteTargetType,
    target_id: str,
    value: ForumVoteValue,
    created_at: datetime,
    updated_at: datetime,
) -> dict:
    db = get_db()

    vote_data = {
        "user_id": ObjectId(user_id),
        "target_type": target_type,
        "target_id": ObjectId(target_id),
        "value": value,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    result = await db.forum_votes.insert_one(vote_data)
    created_vote = await db.forum_votes.find_one({"_id": result.inserted_id})

    if created_vote is None:
        raise RuntimeError("Failed to fetch created vote")

    return created_vote


async def update_vote_value(
    user_id: str,
    target_type: ForumVoteTargetType,
    target_id: str,
    value: ForumVoteValue,
    updated_at: datetime,
) -> dict | None:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(target_id):
        return None

    db = get_db()

    await db.forum_votes.update_one(
        {
            "user_id": ObjectId(user_id),
            "target_type": target_type,
            "target_id": ObjectId(target_id),
        },
        {
            "$set": {
                "value": value,
                "updated_at": updated_at,
            }
        },
    )

    return await db.forum_votes.find_one(
        {
            "user_id": ObjectId(user_id),
            "target_type": target_type,
            "target_id": ObjectId(target_id),
        }
    )


async def delete_vote(
    user_id: str,
    target_type: ForumVoteTargetType,
    target_id: str,
) -> bool:
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(target_id):
        return False

    db = get_db()

    result = await db.forum_votes.delete_one(
        {
            "user_id": ObjectId(user_id),
            "target_type": target_type,
            "target_id": ObjectId(target_id),
        }
    )

    return result.deleted_count > 0


async def delete_votes_for_target(
    target_type: ForumVoteTargetType,
    target_id: str,
) -> int:
    if not ObjectId.is_valid(target_id):
        return 0

    db = get_db()

    result = await db.forum_votes.delete_many(
        {
            "target_type": target_type,
            "target_id": ObjectId(target_id),
        }
    )

    return result.deleted_count


async def delete_votes_for_targets(
    target_type: ForumVoteTargetType,
    target_ids: list[str],
) -> int:
    valid_object_ids = [ObjectId(target_id) for target_id in target_ids if ObjectId.is_valid(target_id)]

    if not valid_object_ids:
        return 0

    db = get_db()

    result = await db.forum_votes.delete_many(
        {
            "target_type": target_type,
            "target_id": {"$in": valid_object_ids},
        }
    )

    return result.deleted_count