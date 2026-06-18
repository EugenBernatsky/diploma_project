from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from app.db.mongo import get_db
from app.schemas.item import Category, ItemSort


def _normalize_search(search: str | None) -> str | None:
    if search is None:
        return None

    normalized = search.strip()
    return normalized if normalized else None


def _normalize_genres(genres: list[str] | None) -> list[str]:
    if not genres:
        return []

    normalized: list[str] = []

    for genre_group in genres:
        normalized.extend(
            genre.strip()
            for genre in genre_group.split(",")
            if genre.strip()
        )

    return normalized


async def _should_search_external_id_exact(db, search_value: str | None) -> bool:
    if search_value is None or ObjectId.is_valid(search_value):
        return False

    if any(char.isspace() for char in search_value):
        return False

    existing_item = await db.media_items.find_one(
        {"external_id": search_value},
        {"_id": 1},
    )
    return existing_item is not None


def _range_filter(
    field_name: str,
    from_value: int | None,
    to_value: int | None,
) -> dict | None:
    bounds: dict = {}

    if from_value is not None:
        bounds["$gte"] = from_value

    if to_value is not None:
        bounds["$lte"] = to_value

    if not bounds:
        return None

    return {field_name: bounds}


def _build_and_query(filters: list[dict]) -> dict:
    if not filters:
        return {}

    if len(filters) == 1:
        return filters[0]

    return {"$and": filters}


def _build_items_query(
    search: str | None = None,
    category: Category | None = None,
    genres: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    runtime_from: int | None = None,
    runtime_to: int | None = None,
    exact_external_id_search: bool = False,
) -> tuple[dict, bool]:
    filters: list[dict] = []
    uses_text_search = False

    search_value = _normalize_search(search)
    if search_value is not None:
        if ObjectId.is_valid(search_value):
            filters.append(
                {
                    "$or": [
                        {"_id": ObjectId(search_value)},
                        {"external_id": search_value},
                    ]
                }
            )
        elif exact_external_id_search:
            filters.append({"external_id": search_value})
        else:
            uses_text_search = True
            filters.append({"$text": {"$search": search_value}})

    if category is not None:
        filters.append({"category": category})

    genre_filters = _normalize_genres(genres)
    if genre_filters:
        filters.append({"genres": {"$all": genre_filters}})

    year_filter = _range_filter("year", year_from, year_to)
    if year_filter is not None:
        filters.append(year_filter)

    runtime_filter = _range_filter("runtime", runtime_from, runtime_to)
    if runtime_filter is not None:
        filters.append(runtime_filter)

    if min_rating is not None:
        filters.append(
            {
                "$or": [
                    {"tmdb_vote_average": {"$gte": min_rating}},
                    {"book_rating_average": {"$gte": min_rating}},
                ]
            }
        )

    return _build_and_query(filters), uses_text_search


def _build_sort(sort: ItemSort, uses_text_search: bool) -> tuple[dict | None, list[tuple]]:
    if sort == "relevance" and uses_text_search:
        return (
            {"score": {"$meta": "textScore"}},
            [
                ("score", {"$meta": "textScore"}),
                ("created_at", DESCENDING),
                ("_id", DESCENDING),
            ],
        )

    if sort in {"relevance", "newest"}:
        return None, [("created_at", DESCENDING), ("_id", DESCENDING)]

    if sort == "updated":
        return None, [
            ("updated_at", DESCENDING),
            ("created_at", DESCENDING),
            ("_id", DESCENDING),
        ]

    if sort == "title_asc":
        return None, [("title", ASCENDING), ("_id", ASCENDING)]

    if sort == "title_desc":
        return None, [("title", DESCENDING), ("_id", DESCENDING)]

    if sort == "year_asc":
        return None, [("year", ASCENDING), ("_id", ASCENDING)]

    if sort == "year_desc":
        return None, [("year", DESCENDING), ("_id", DESCENDING)]

    if sort == "rating_asc":
        return None, [
            ("tmdb_vote_average", ASCENDING),
            ("book_rating_average", ASCENDING),
            ("_id", ASCENDING),
        ]

    return None, [
        ("tmdb_vote_average", DESCENDING),
        ("book_rating_average", DESCENDING),
        ("_id", DESCENDING),
    ]


async def find_items(
    search: str | None = None,
    category: Category | None = None,
    genres: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    runtime_from: int | None = None,
    runtime_to: int | None = None,
    sort: ItemSort = "newest",
    limit: int = 100,
    skip: int = 0,
) -> list[dict]:
    db = get_db()
    search_value = _normalize_search(search)
    exact_external_id_search = await _should_search_external_id_exact(
        db,
        search_value,
    )

    query, uses_text_search = _build_items_query(
        search=search_value,
        category=category,
        genres=genres,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime_from=runtime_from,
        runtime_to=runtime_to,
        exact_external_id_search=exact_external_id_search,
    )
    projection, sort_spec = _build_sort(sort, uses_text_search)
    cursor = db.media_items.find(query, projection)

    return await cursor.sort(sort_spec).skip(skip).limit(limit).to_list(length=limit)


async def count_items(
    search: str | None = None,
    category: Category | None = None,
    genres: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    runtime_from: int | None = None,
    runtime_to: int | None = None,
) -> int:
    db = get_db()
    search_value = _normalize_search(search)
    exact_external_id_search = await _should_search_external_id_exact(
        db,
        search_value,
    )

    query, _uses_text_search = _build_items_query(
        search=search_value,
        category=category,
        genres=genres,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime_from=runtime_from,
        runtime_to=runtime_to,
        exact_external_id_search=exact_external_id_search,
    )

    return await db.media_items.count_documents(query)


async def find_item_by_id(item_id: str) -> dict | None:
    if not ObjectId.is_valid(item_id):
        return None

    db = get_db()
    return await db.media_items.find_one({"_id": ObjectId(item_id)})


async def find_items_by_ids(item_ids: list[str]) -> list[dict]:
    valid_object_ids = [ObjectId(item_id) for item_id in item_ids if ObjectId.is_valid(item_id)]

    if not valid_object_ids:
        return []

    db = get_db()
    return await db.media_items.find({"_id": {"$in": valid_object_ids}}).to_list(length=len(valid_object_ids))


async def insert_item(item_data: dict) -> dict:
    db = get_db()

    result = await db.media_items.insert_one(item_data)
    created_item = await db.media_items.find_one({"_id": result.inserted_id})

    if created_item is None:
        raise RuntimeError("Failed to fetch created item")

    return created_item


async def update_item_by_id(item_id: str, item_data: dict) -> dict | None:
    if not ObjectId.is_valid(item_id):
        return None

    db = get_db()

    await db.media_items.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": item_data},
    )

    return await db.media_items.find_one({"_id": ObjectId(item_id)})


async def delete_item_by_id(item_id: str) -> bool:
    if not ObjectId.is_valid(item_id):
        return False

    db = get_db()

    result = await db.media_items.delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count > 0
