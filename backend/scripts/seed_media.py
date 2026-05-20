import asyncio
from datetime import datetime, UTC

from pymongo import AsyncMongoClient

from app.core.config import settings


SEED_MEDIA_ITEMS = [
    {
        "title": "Interstellar",
        "category": "movie",
        "year": 2014,
        "genres": ["Sci-Fi", "Drama"],
        "description": "Фільм про космічну подорож, виживання людства та пошук нового дому.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
    {
        "title": "Inception",
        "category": "movie",
        "year": 2010,
        "genres": ["Sci-Fi", "Thriller"],
        "description": "Історія про проникнення у сни та маніпуляцію ідеями.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
    {
        "title": "Breaking Bad",
        "category": "series",
        "year": 2008,
        "genres": ["Crime", "Drama"],
        "description": "Серіал про вчителя хімії, який занурюється у кримінальний світ.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
    {
        "title": "Dark",
        "category": "series",
        "year": 2017,
        "genres": ["Sci-Fi", "Mystery"],
        "description": "Похмурий серіал про час, сімейні таємниці й зникнення дітей.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
    {
        "title": "1984",
        "category": "book",
        "year": 1949,
        "genres": ["Dystopian", "Political Fiction"],
        "description": "Роман про тоталітарну державу, контроль і втрату свободи.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
    {
        "title": "Dune",
        "category": "book",
        "year": 1965,
        "genres": ["Sci-Fi", "Adventure"],
        "description": "Епічний науково-фантастичний роман про владу, ресурси та пророцтво.",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    },
]


async def seed_media():
    client = AsyncMongoClient(settings.MONGODB_URL)

    try:
        db = client[settings.MONGODB_DB]
        collection = db.media_items

        delete_result = await collection.delete_many({})
        insert_result = await collection.insert_many(SEED_MEDIA_ITEMS)

        print(f"Deleted documents: {delete_result.deleted_count}")
        print(f"Inserted documents: {len(insert_result.inserted_ids)}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(seed_media())