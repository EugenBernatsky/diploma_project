from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.favorites_repository import (
    delete_favorite,
    find_favorite,
    find_favorite_item_ids_by_user,
    insert_favorite,
)
from app.repositories.items_repository import find_item_by_id, find_items_by_ids
from app.schemas.favorite import FavoriteActionResponse
from app.schemas.item import MediaItem


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


async def get_favorites(user_id: str) -> list[MediaItem]:
    item_ids = await find_favorite_item_ids_by_user(user_id)

    if not item_ids:
        return []

    docs = await find_items_by_ids(item_ids)
    docs_by_id = {str(doc["_id"]): doc for doc in docs}

    ordered_docs = [docs_by_id[item_id] for item_id in item_ids if item_id in docs_by_id]

    return [_map_doc_to_media_item(doc) for doc in ordered_docs]


async def add_to_favorites(user_id: str, item_id: str) -> FavoriteActionResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_favorite = await find_favorite(user_id, item_id)
    if existing_favorite is not None:
        raise HTTPException(status_code=400, detail="Item already in favorites")

    await insert_favorite(
        user_id=user_id,
        item_id=item_id,
        created_at=datetime.now(UTC),
    )

    return FavoriteActionResponse(message="Item added to favorites")


async def remove_from_favorites(user_id: str, item_id: str) -> FavoriteActionResponse:
    deleted = await delete_favorite(user_id, item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite not found")

    return FavoriteActionResponse(message="Item removed from favorites")