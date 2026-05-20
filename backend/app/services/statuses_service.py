from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.items_repository import find_item_by_id, find_items_by_ids
from app.repositories.statuses_repository import (
    delete_status,
    find_status,
    find_status_docs_by_user,
    upsert_status,
)
from app.schemas.status import (
    MediaItemWithStatus,
    StatusActionResponse,
    StatusPayload,
    UserItemStatusResponse,
)


def _map_doc_to_media_item_with_status(doc: dict, status: str) -> MediaItemWithStatus:
    return MediaItemWithStatus(
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
        status=status,
        viewability=doc.get("viewability"),
        access_view_status=doc.get("access_view_status"),
        epub_available=doc.get("epub_available"),
        pdf_available=doc.get("pdf_available"),
    )

async def get_my_status(user_id: str, item_id: str) -> UserItemStatusResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    status_doc = await find_status(user_id, item_id)
    if status_doc is None:
        raise HTTPException(status_code=404, detail="Status not found")

    return UserItemStatusResponse(
        item_id=item_id,
        status=status_doc["status"],
    )


async def set_status(user_id: str, item_id: str, payload: StatusPayload) -> StatusActionResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await upsert_status(
        user_id=user_id,
        item_id=item_id,
        status=payload.status,
        now=datetime.now(UTC),
    )

    return StatusActionResponse(message="Status saved successfully")


async def remove_status(user_id: str, item_id: str) -> StatusActionResponse:
    deleted = await delete_status(user_id, item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Status not found")

    return StatusActionResponse(message="Status removed successfully")


async def get_statuses(user_id: str, status: str | None = None) -> list[MediaItemWithStatus]:
    status_docs = await find_status_docs_by_user(user_id, status)

    if not status_docs:
        return []

    item_ids = [str(doc["item_id"]) for doc in status_docs]
    items = await find_items_by_ids(item_ids)
    items_by_id = {str(doc["_id"]): doc for doc in items}

    result: list[MediaItemWithStatus] = []

    for status_doc in status_docs:
        item_id = str(status_doc["item_id"])
        item_doc = items_by_id.get(item_id)

        if item_doc is None:
            continue

        result.append(
            _map_doc_to_media_item_with_status(
                item_doc,
                status_doc["status"],
            )
        )

    return result