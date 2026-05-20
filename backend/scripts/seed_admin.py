import asyncio
from datetime import UTC, datetime

from pymongo import AsyncMongoClient

from app.core.config import settings
from app.core.profile_defaults import (
    DEFAULT_AVATAR_ID,
    get_default_notification_settings,
)
from app.core.security import hash_password


async def seed_admin():
    client = AsyncMongoClient(settings.MONGODB_URL)

    try:
        db = client[settings.MONGODB_DB]

        existing_admin = await db.users.find_one({"email": settings.ADMIN_EMAIL})
        if existing_admin is not None:
            print("Admin already exists")
            return

        now = datetime.now(UTC)

        admin_data = {
            "username": settings.ADMIN_USERNAME,
            "email": settings.ADMIN_EMAIL,
            "password_hash": hash_password(settings.ADMIN_PASSWORD),
            "role": "admin",
            "is_active": True,
            "avatar_id": DEFAULT_AVATAR_ID,
            "notification_settings": get_default_notification_settings(),
            "created_at": now,
            "updated_at": now,
        }

        await db.users.insert_one(admin_data)
        print("Admin user created successfully")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(seed_admin())