from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.comments_repository import delete_comments_by_item_id
from app.repositories.favorites_repository import delete_favorites_by_item_id
from app.repositories.interactions_repository import delete_interactions_by_item_id
from app.repositories.items_repository import (
    delete_item_by_id,
    find_item_by_id,
    find_items,
    insert_item,
    update_item_by_id,
)
from app.repositories.notifications_repository import delete_notifications_by_item_id
from app.repositories.ratings_repository import delete_ratings_by_item_id
from app.repositories.statuses_repository import delete_statuses_by_item_id
from app.schemas.item import (
    Category,
    EpisodeShortInfo,
    IndustryIdentifier,
    ItemActionResponse,
    LocalizedItemContent,
    MediaItem,
    MediaItemCreate,
    MediaItemUpdate,
    PurchaseLink,
    TrailerLink,
    WatchLink,
)


def _normalize_required_text(value: str, field_name: str) -> str:
    normalized = value.strip()

    if not normalized:
        raise HTTPException(status_code=400, detail=f"{field_name} cannot be empty")

    return normalized


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized if normalized else None


def _normalize_genres(genres: list[str]) -> list[str]:
    return [genre.strip() for genre in genres if genre.strip()]


def _normalize_string_list(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]


def _normalize_trailers(trailers: list[TrailerLink]) -> list[dict]:
    normalized: list[dict] = []

    for trailer in trailers:
        name = trailer.name.strip()
        url = trailer.url.strip()

        if not name or not url:
            continue

        normalized.append(
            {
                "name": name,
                "site": _normalize_optional_text(trailer.site),
                "url": url,
                "language": _normalize_optional_text(trailer.language),
            }
        )

    return normalized


def _normalize_watch_links(watch_links: list[WatchLink]) -> list[dict]:
    normalized: list[dict] = []

    for link in watch_links:
        provider_name = link.provider_name.strip()
        url = link.url.strip()

        if not provider_name or not url:
            continue

        normalized.append(
            {
                "provider_name": provider_name,
                "provider_type": _normalize_optional_text(link.provider_type),
                "region": _normalize_optional_text(link.region),
                "url": url,
            }
        )

    return normalized


def _normalize_purchase_links(purchase_links: list[PurchaseLink]) -> list[dict]:
    normalized: list[dict] = []

    for link in purchase_links:
        url = link.url.strip()
        store_name = _normalize_optional_text(link.store_name)
        provider_name = (
            _normalize_optional_text(link.provider_name)
            or store_name
            or "External"
        )
        provider_type = _normalize_optional_text(link.provider_type) or "external"

        if not url:
            continue

        normalized.append(
            {
                "provider_name": provider_name,
                "provider_type": provider_type,
                "store_name": store_name,
                "region": _normalize_optional_text(link.region),
                "url": url,
                "price": link.price,
                "currency": _normalize_optional_text(link.currency),
            }
        )

    return normalized


def _normalize_episode_info(episode: EpisodeShortInfo | None) -> dict | None:
    if episode is None:
        return None

    return {
        "name": _normalize_optional_text(episode.name),
        "air_date": _normalize_optional_text(episode.air_date),
        "episode_number": episode.episode_number,
        "season_number": episode.season_number,
        "runtime": episode.runtime,
        "overview": _normalize_optional_text(episode.overview),
        "still_url": _normalize_optional_text(episode.still_url),
    }


def _normalize_localized(localized: dict[str, LocalizedItemContent]) -> dict[str, dict]:
    normalized: dict[str, dict] = {}

    for locale, content in localized.items():
        locale_key = locale.strip()
        if not locale_key:
            continue

        normalized_content = {
            "title": _normalize_optional_text(content.title),
            "description": _normalize_optional_text(content.description),
            "tagline": _normalize_optional_text(content.tagline),
        }

        if any(value is not None for value in normalized_content.values()):
            normalized[locale_key] = normalized_content

    return normalized


def _normalize_industry_identifiers(
    identifiers: list[IndustryIdentifier],
) -> list[dict]:
    normalized: list[dict] = []

    for item in identifiers:
        item_type = item.type.strip()
        identifier = item.identifier.strip()

        if not item_type or not identifier:
            continue

        normalized.append(
            {
                "type": item_type,
                "identifier": identifier,
            }
        )

    return normalized


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


def _build_item_data(payload: MediaItemCreate | MediaItemUpdate) -> dict:
    return {
        "title": _normalize_required_text(payload.title, "Title"),
        "category": payload.category,
        "year": payload.year,
        "genres": _normalize_genres(payload.genres),
        "description": _normalize_required_text(payload.description, "Description"),
        "poster_url": _normalize_optional_text(payload.poster_url),
        "backdrop_url": _normalize_optional_text(payload.backdrop_url),
        "external_source": _normalize_optional_text(payload.external_source),
        "external_id": _normalize_optional_text(payload.external_id),
        "original_title": _normalize_optional_text(payload.original_title),
        "original_name": _normalize_optional_text(payload.original_name),
        "original_language": _normalize_optional_text(payload.original_language),
        "release_date": _normalize_optional_text(payload.release_date),
        "first_air_date": _normalize_optional_text(payload.first_air_date),
        "tagline": _normalize_optional_text(payload.tagline),
        "content_status": _normalize_optional_text(payload.content_status),
        "homepage": _normalize_optional_text(payload.homepage),
        "production_countries": _normalize_string_list(payload.production_countries),
        "tmdb_vote_average": payload.tmdb_vote_average,
        "tmdb_vote_count": payload.tmdb_vote_count,
        "runtime": payload.runtime,
        "imdb_id": _normalize_optional_text(payload.imdb_id),
        "episode_run_time": payload.episode_run_time,
        "number_of_seasons": payload.number_of_seasons,
        "number_of_episodes": payload.number_of_episodes,
        "networks": _normalize_string_list(payload.networks),

        "subtitle": _normalize_optional_text(payload.subtitle),
        "authors": _normalize_string_list(payload.authors),
        "publisher": _normalize_optional_text(payload.publisher),
        "published_date": _normalize_optional_text(payload.published_date),
        "page_count": payload.page_count,
        "industry_identifiers": _normalize_industry_identifiers(payload.industry_identifiers),
        "book_rating_average": payload.book_rating_average,
        "book_ratings_count": payload.book_ratings_count,
        "preview_link": _normalize_optional_text(payload.preview_link),
        "info_link": _normalize_optional_text(payload.info_link),
        "canonical_link": _normalize_optional_text(payload.canonical_link),
        "web_reader_link": _normalize_optional_text(payload.web_reader_link),
        "saleability": _normalize_optional_text(payload.saleability),
        "is_ebook": payload.is_ebook,

        "next_episode_to_air": _normalize_episode_info(payload.next_episode_to_air),
        "last_episode_to_air": _normalize_episode_info(payload.last_episode_to_air),
        "localized": _normalize_localized(payload.localized),
        "trailers": _normalize_trailers(payload.trailers),
        "watch_links": _normalize_watch_links(payload.watch_links),
        "purchase_links": _normalize_purchase_links(payload.purchase_links),

        "viewability": _normalize_optional_text(payload.viewability),
        "access_view_status": _normalize_optional_text(payload.access_view_status),
        "epub_available": payload.epub_available,
        "pdf_available": payload.pdf_available,
    }


async def get_items_for_admin(
    category: Category | None = None,
    limit: int = 200,
) -> list[MediaItem]:
    docs = await find_items(category=category, limit=limit)
    return [_map_doc_to_media_item(doc) for doc in docs]


async def create_item_admin(payload: MediaItemCreate) -> MediaItem:
    now = datetime.now(UTC)

    item_data = _build_item_data(payload)
    item_data["created_at"] = now
    item_data["updated_at"] = now

    created_item = await insert_item(item_data)
    return _map_doc_to_media_item(created_item)


async def update_item_admin(item_id: str, payload: MediaItemUpdate) -> MediaItem:
    existing_item = await find_item_by_id(item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = _build_item_data(payload)
    item_data["updated_at"] = datetime.now(UTC)

    updated_item = await update_item_by_id(item_id, item_data)

    if updated_item is None:
        raise RuntimeError("Failed to fetch updated item")

    return _map_doc_to_media_item(updated_item)


async def delete_item_admin(item_id: str) -> ItemActionResponse:
    existing_item = await find_item_by_id(item_id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted = await delete_item_by_id(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    await delete_favorites_by_item_id(item_id)
    await delete_ratings_by_item_id(item_id)
    await delete_statuses_by_item_id(item_id)
    await delete_interactions_by_item_id(item_id)
    await delete_comments_by_item_id(item_id)
    await delete_notifications_by_item_id(item_id)

    return ItemActionResponse(message="Item deleted by admin")
