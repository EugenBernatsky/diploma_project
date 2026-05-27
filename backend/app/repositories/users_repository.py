from bson import ObjectId

from app.db.mongo import get_db


async def find_user_by_email(email: str) -> dict | None:
    db = get_db()
    return await db.users.find_one({"email": email})


async def find_user_by_username(username: str) -> dict | None:
    db = get_db()
    return await db.users.find_one({"username": username})


async def find_user_by_id(user_id: str) -> dict | None:
    if not ObjectId.is_valid(user_id):
        return None

    db = get_db()
    return await db.users.find_one({"_id": ObjectId(user_id)})


async def insert_user(user_data: dict) -> dict:
    db = get_db()
    result = await db.users.insert_one(user_data)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    if created_user is None:
        raise RuntimeError("Failed to fetch created user")

    return created_user


async def update_user_fields(user_id: str, update_data: dict) -> dict | None:
    if not ObjectId.is_valid(user_id):
        return None

    db = get_db()

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    return await db.users.find_one({"_id": ObjectId(user_id)})

async def find_user_by_username_except_user(
    username: str,
    user_id: str,
) -> dict | None:
    if not ObjectId.is_valid(user_id):
        return None

    db = get_db()

    return await db.users.find_one(
        {
            "username": username,
            "_id": {"$ne": ObjectId(user_id)},
        }
    )