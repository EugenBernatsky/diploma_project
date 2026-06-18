from fastapi import HTTPException

from app.repositories.comments_repository import count_comments_by_item_id
from app.repositories.favorites_repository import count_favorites_by_item_id
from app.repositories.items_repository import count_items, find_item_by_id, find_items
from app.repositories.ratings_repository import get_rating_stats_by_item_id
from app.repositories.statuses_repository import count_statuses_by_item_id
from app.schemas.item import (
    Category,
    ItemSort,
    ItemStatsResponse,
    ItemsCountResponse,
    ItemsListResponse,
    MediaItem,
)

def _map_doc_to_media_item(doc: dict) -> MediaItem:
    return MediaItem(
        id=str(doc["_id"]),
        title=doc["title"],
        category=doc["category"],
        year=doc["year"],
        genres=doc["genres"],
        description=doc["description"],
        poster_url=doc.get("poster_url"),
        backdrop_url=doc.get("backdrop_url"),
        external_source=doc.get("external_source"),
        external_id=doc.get("external_id"),
        original_title=doc.get("original_title"),
        original_name=doc.get("original_name"),
        original_language=doc.get("original_language"),
        release_date=doc.get("release_date"),
        first_air_date=doc.get("first_air_date"),
        tagline=doc.get("tagline"),
        content_status=doc.get("content_status") or doc.get("status"),
        homepage=doc.get("homepage"),
        production_countries=doc.get("production_countries", []),
        tmdb_vote_average=doc.get("tmdb_vote_average"),
        tmdb_vote_count=doc.get("tmdb_vote_count"),
        runtime=doc.get("runtime"),
        imdb_id=doc.get("imdb_id"),
        episode_run_time=doc.get("episode_run_time", []),
        number_of_seasons=doc.get("number_of_seasons"),
        number_of_episodes=doc.get("number_of_episodes"),
        networks=doc.get("networks", []),
        next_episode_to_air=doc.get("next_episode_to_air"),
        last_episode_to_air=doc.get("last_episode_to_air"),
        subtitle=doc.get("subtitle"),
        authors=doc.get("authors", []),
        publisher=doc.get("publisher"),
        published_date=doc.get("published_date"),
        page_count=doc.get("page_count"),
        industry_identifiers=doc.get("industry_identifiers", []),
        book_rating_average=doc.get("book_rating_average"),
        book_ratings_count=doc.get("book_ratings_count"),
        preview_link=doc.get("preview_link"),
        info_link=doc.get("info_link"),
        canonical_link=doc.get("canonical_link"),
        web_reader_link=doc.get("web_reader_link"),
        saleability=doc.get("saleability"),
        is_ebook=doc.get("is_ebook"),
        localized=doc.get("localized", {}),
        trailers=doc.get("trailers", []),
        watch_links=doc.get("watch_links", []),
        purchase_links=doc.get("purchase_links", []),
        viewability=doc.get("viewability"),
        access_view_status=doc.get("access_view_status"),
        epub_available=doc.get("epub_available"),
        pdf_available=doc.get("pdf_available"),
    )


async def get_items(
    search: str | None = None,
    category: Category | None = None,
    genres: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    min_rating: float | None = None,
    runtime_from: int | None = None,
    runtime_to: int | None = None,
    sort: ItemSort = "relevance",
    limit: int = 20,
    skip: int = 0,
) -> ItemsListResponse:
    total = await count_items(
        search=search,
        category=category,
        genres=genres,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime_from=runtime_from,
        runtime_to=runtime_to,
    )
    docs = await find_items(
        search=search,
        category=category,
        genres=genres,
        year_from=year_from,
        year_to=year_to,
        min_rating=min_rating,
        runtime_from=runtime_from,
        runtime_to=runtime_to,
        sort=sort,
        limit=limit,
        skip=skip,
    )

    return ItemsListResponse(
        results=[_map_doc_to_media_item(doc) for doc in docs],
        total=total,
        limit=limit,
        skip=skip,
    )

async def get_items_count(category: Category | None = None) -> ItemsCountResponse:
    count = await count_items(category=category)
    return ItemsCountResponse(count=count)

async def get_item_by_id(item_id: str) -> MediaItem | None:
    doc = await find_item_by_id(item_id)

    if doc is None:
        return None

    return _map_doc_to_media_item(doc)

async def get_item_stats(item_id: str) -> ItemStatsResponse:
    item = await find_item_by_id(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    rating_stats = await get_rating_stats_by_item_id(item_id)
    favorites_count = await count_favorites_by_item_id(item_id)
    status_counts = await count_statuses_by_item_id(item_id)
    comments_count = await count_comments_by_item_id(item_id)

    return ItemStatsResponse(
        item_id=item_id,
        user_rating_average=rating_stats["average"],
        user_ratings_count=rating_stats["count"],
        favorites_count=favorites_count,
        statuses_total_count=sum(status_counts.values()),
        status_counts=status_counts,
        comments_count=comments_count,
    )
