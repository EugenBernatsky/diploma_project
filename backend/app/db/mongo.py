from pymongo import AsyncMongoClient

from app.core.config import settings

client: AsyncMongoClient | None = None


async def connect_to_mongo():
    global client
    client = AsyncMongoClient(settings.MONGODB_URL)
    await client.admin.command("ping")


def get_db():
    if client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return client[settings.MONGODB_DB]


async def close_mongo_connection():
    global client
    if client is not None:
        await client.close()
        client = None