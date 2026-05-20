from app.repositories.items_repository import find_item_by_id, find_items
from app.schemas.item import MediaItem, Category


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


async def get_items(category: Category | None = None) -> list[MediaItem]:
    docs = await find_items(category, limit=100)
    return [_map_doc_to_media_item(doc) for doc in docs]


async def get_item_by_id(item_id: str) -> MediaItem | None:
    doc = await find_item_by_id(item_id)

    if doc is None:
        return None

    return _map_doc_to_media_item(doc)