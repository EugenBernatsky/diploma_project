import re
from typing import Any

from bson import ObjectId
from pymongo import DESCENDING

from app.db.mongo import get_db
from app.schemas.item import Category


def _safe_regex(value: str) -> dict:
    return {"$regex": re.escape(value), "$options": "i"}


def _normalize_search(search: str | None) -> str | None:
    if search is None:
        return None

    normalized = search.strip()

    return normalized or None


def _build_and_query(filters: list[dict]) -> dict:
    if not filters:
        return {}

    if len(filters) == 1:
        return filters[0]

    return {"$and": filters}


def _optional_object_id(value: str | None) -> ObjectId | None:
    if value and ObjectId.is_valid(value):
        return ObjectId(value)

    return None


async def find_admin_items(
    search: str | None = None,
    category: Category | None = None,
    limit: int = 20,
    skip: int = 0,
) -> tuple[list[dict], int]:
    db = get_db()

    filters: list[dict] = []

    if category is not None:
        filters.append({"category": category})

    normalized_search = _normalize_search(search)

    if normalized_search:
        if ObjectId.is_valid(normalized_search):
            filters.append(
                {
                    "$or": [
                        {"_id": ObjectId(normalized_search)},
                        {"external_id": normalized_search},
                    ]
                }
            )
        elif normalized_search.isdigit():
            filters.append({"external_id": normalized_search})
        else:
            filters.append({"$text": {"$search": normalized_search}})

    query = _build_and_query(filters)

    total = await db.media_items.count_documents(query)

    cursor = db.media_items.find(
        query,
        {
            "score": {"$meta": "textScore"},
        } if normalized_search and not ObjectId.is_valid(normalized_search) and not normalized_search.isdigit() else None,
    )

    if normalized_search and not ObjectId.is_valid(normalized_search) and not normalized_search.isdigit():
        cursor = cursor.sort(
            [
                ("score", {"$meta": "textScore"}),
                ("updated_at", DESCENDING),
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ]
        )
    else:
        cursor = cursor.sort(
            [
                ("updated_at", DESCENDING),
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ]
        )

    docs = await cursor.skip(skip).limit(limit).to_list(length=limit)

    return docs, total


async def find_admin_comments(
    search: str | None = None,
    item_id: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> tuple[list[dict], int]:
    db = get_db()

    filters: list[dict[str, Any]] = []

    item_object_id = _optional_object_id(item_id)
    if item_object_id is not None:
        filters.append({"item_id": item_object_id})

    user_object_id = _optional_object_id(user_id)
    if user_object_id is not None:
        filters.append({"user_id": user_object_id})

    normalized_search = _normalize_search(search)

    is_text_search = False

    if normalized_search:
        if ObjectId.is_valid(normalized_search):
            search_object_id = ObjectId(normalized_search)
            filters.append(
                {
                    "$or": [
                        {"_id": search_object_id},
                        {"user_id": search_object_id},
                        {"item_id": search_object_id},
                    ]
                }
            )
        else:
            filters.append({"$text": {"$search": normalized_search}})
            is_text_search = True

    query = _build_and_query(filters)

    total = await db.comments.count_documents(query)

    pipeline: list[dict] = [
        {"$match": query},
    ]

    if is_text_search:
        pipeline.append(
            {
                "$sort": {
                    "score": {"$meta": "textScore"},
                    "created_at": -1,
                    "_id": -1,
                }
            }
        )
    else:
        pipeline.append({"$sort": {"created_at": -1, "_id": -1}})

    pipeline.extend(
        [
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "media_items",
                    "localField": "item_id",
                    "foreignField": "_id",
                    "as": "item",
                }
            },
            {
                "$unwind": {
                    "path": "$item",
                    "preserveNullAndEmptyArrays": True,
                }
            },
        ]
    )

    cursor = await db.comments.aggregate(pipeline)
    docs = await cursor.to_list(length=limit)

    return docs, total


async def find_admin_forum_threads(
    search: str | None = None,
    category: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> tuple[list[dict], int]:
    db = get_db()

    filters: list[dict[str, Any]] = []

    if category:
        filters.append({"category_type": category})

    user_object_id = _optional_object_id(user_id)
    if user_object_id is not None:
        filters.append({"user_id": user_object_id})

    normalized_search = _normalize_search(search)

    is_text_search = False

    if normalized_search:
        if ObjectId.is_valid(normalized_search):
            search_object_id = ObjectId(normalized_search)
            filters.append(
                {
                    "$or": [
                        {"_id": search_object_id},
                        {"user_id": search_object_id},
                    ]
                }
            )
        else:
            filters.append({"$text": {"$search": normalized_search}})
            is_text_search = True

    query = _build_and_query(filters)

    total = await db.forum_threads.count_documents(query)

    cursor = db.forum_threads.find(
        query,
        {
            "score": {"$meta": "textScore"},
        } if is_text_search else None,
    )

    if is_text_search:
        cursor = cursor.sort(
            [
                ("score", {"$meta": "textScore"}),
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ]
        )
    else:
        cursor = cursor.sort(
            [
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ]
        )

    docs = await cursor.skip(skip).limit(limit).to_list(length=limit)

    return docs, total


async def find_admin_forum_posts(
    search: str | None = None,
    thread_id: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> tuple[list[dict], int]:
    db = get_db()

    filters: list[dict[str, Any]] = []

    thread_object_id = _optional_object_id(thread_id)
    if thread_object_id is not None:
        filters.append({"thread_id": thread_object_id})

    user_object_id = _optional_object_id(user_id)
    if user_object_id is not None:
        filters.append({"user_id": user_object_id})

    normalized_search = _normalize_search(search)

    is_text_search = False

    if normalized_search:
        if ObjectId.is_valid(normalized_search):
            search_object_id = ObjectId(normalized_search)
            filters.append(
                {
                    "$or": [
                        {"_id": search_object_id},
                        {"user_id": search_object_id},
                        {"thread_id": search_object_id},
                    ]
                }
            )
        else:
            filters.append({"$text": {"$search": normalized_search}})
            is_text_search = True

    query = _build_and_query(filters)

    total = await db.forum_posts.count_documents(query)

    pipeline: list[dict] = [
        {"$match": query},
    ]

    if is_text_search:
        pipeline.append(
            {
                "$sort": {
                    "score": {"$meta": "textScore"},
                    "created_at": -1,
                    "_id": -1,
                }
            }
        )
    else:
        pipeline.append({"$sort": {"created_at": -1, "_id": -1}})

    pipeline.extend(
        [
            {"$skip": skip},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "forum_threads",
                    "localField": "thread_id",
                    "foreignField": "_id",
                    "as": "thread",
                }
            },
            {
                "$unwind": {
                    "path": "$thread",
                    "preserveNullAndEmptyArrays": True,
                }
            },
        ]
    )

    cursor = await db.forum_posts.aggregate(pipeline)
    docs = await cursor.to_list(length=limit)

    return docs, total


async def get_admin_dashboard_counts() -> dict:
    db = get_db()

    users_count = await db.users.count_documents({})
    items_count = await db.media_items.count_documents({})
    comments_count = await db.comments.count_documents({})
    forum_threads_count = await db.forum_threads.count_documents({})
    forum_posts_count = await db.forum_posts.count_documents({})
    unread_notifications_count = await db.notifications.count_documents({"is_read": False})

    return {
        "users_count": users_count,
        "items_count": items_count,
        "comments_count": comments_count,
        "forum_threads_count": forum_threads_count,
        "forum_posts_count": forum_posts_count,
        "unread_notifications_count": unread_notifications_count,
    }