import argparse
import asyncio
from datetime import UTC, datetime

import httpx
from pymongo import AsyncMongoClient

from app.core.config import settings

import html
import re


def extract_year(date_str: str | None) -> int:
    if not date_str or len(date_str) < 4:
        return 0

    try:
        return int(date_str[:4])
    except ValueError:
        return 0


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized if normalized else None

def normalize_url(value: str | None) -> str | None:
    normalized = normalize_text(value)
    if normalized is None:
        return None

    if normalized.startswith("http://"):
        return "https://" + normalized[len("http://"):]
    return normalized


def clean_html_text(value: str | None) -> str | None:
    normalized = normalize_text(value)
    if normalized is None:
        return None

    text = re.sub(r"(?i)<br\s*/?>", "\n", normalized)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip() or None


def normalize_string_list(values: list[str] | None) -> list[str]:
    if not values:
        return []

    return [value.strip() for value in values if value and value.strip()]


def map_industry_identifiers(volume_info: dict) -> list[dict]:
    identifiers = volume_info.get("industryIdentifiers", [])
    result: list[dict] = []

    for item in identifiers:
        item_type = normalize_text(item.get("type"))
        identifier = normalize_text(item.get("identifier"))

        if not item_type or not identifier:
            continue

        result.append(
            {
                "type": item_type,
                "identifier": identifier,
            }
        )

    return result


def pick_book_poster(volume_info: dict) -> str | None:
    image_links = volume_info.get("imageLinks", {})

    for key in [
        "extraLarge",
        "large",
        "medium",
        "small",
        "thumbnail",
        "smallThumbnail",
    ]:
        url = image_links.get(key)
        if url:
            return normalize_url(url)

    return None


def map_purchase_links(sale_info: dict) -> list[dict]:
    buy_link = normalize_url(sale_info.get("buyLink"))
    if not buy_link:
        return []

    retail_price = sale_info.get("retailPrice") or {}
    amount = retail_price.get("amount")
    currency = retail_price.get("currencyCode")

    return [
        {
            "store_name": "Google Books",
            "region": sale_info.get("country"),
            "url": buy_link,
            "price": amount,
            "currency": currency,
        }
    ]


def map_localized(volume_info: dict) -> dict[str, dict]:
    language = normalize_text(volume_info.get("language")) or settings.GOOGLE_BOOKS_LANG

    return {
        language: {
            "title": normalize_text(volume_info.get("title")),
            "description": clean_html_text(volume_info.get("description")),
            "tagline": None,
        }
    }


def map_book_item(volume: dict) -> dict:
    volume_info = volume.get("volumeInfo", {})
    sale_info = volume.get("saleInfo", {})
    access_info = volume.get("accessInfo", {})

    title = normalize_text(volume_info.get("title")) or "Untitled"

    return {
        "title": title,
        "category": "book",
        "year": extract_year(volume_info.get("publishedDate")),
        "genres": normalize_string_list(volume_info.get("categories")),
        "description": clean_html_text(volume_info.get("description")) or "",
        "poster_url": pick_book_poster(volume_info),
        "backdrop_url": None,
        "external_source": "google_books",
        "external_id": str(volume["id"]),
        "original_title": None,
        "original_name": None,
        "original_language": normalize_text(volume_info.get("language")),
        "release_date": None,
        "first_air_date": None,
        "tagline": None,
        "content_status": None,
        "homepage": normalize_url(volume_info.get("canonicalVolumeLink"))
        or normalize_url(volume_info.get("infoLink")),
        "production_countries": [],
        "tmdb_vote_average": None,
        "tmdb_vote_count": None,
        "runtime": None,
        "imdb_id": None,
        "episode_run_time": [],
        "number_of_seasons": None,
        "number_of_episodes": None,
        "networks": [],
        "next_episode_to_air": None,
        "last_episode_to_air": None,
        "subtitle": normalize_text(volume_info.get("subtitle")),
        "authors": normalize_string_list(volume_info.get("authors")),
        "publisher": normalize_text(volume_info.get("publisher")),
        "published_date": normalize_text(volume_info.get("publishedDate")),
        "page_count": volume_info.get("pageCount"),
        "industry_identifiers": map_industry_identifiers(volume_info),
        "book_rating_average": volume_info.get("averageRating"),
        "book_ratings_count": volume_info.get("ratingsCount"),
        "preview_link": normalize_url(volume_info.get("previewLink")),
        "info_link": normalize_url(volume_info.get("infoLink")),
        "canonical_link": normalize_url(volume_info.get("canonicalVolumeLink")),
        "web_reader_link": normalize_url(access_info.get("webReaderLink")),
        "saleability": normalize_text(sale_info.get("saleability")),
        "is_ebook": sale_info.get("isEbook"),
        "viewability": normalize_text(access_info.get("viewability")),
        "access_view_status": normalize_text(access_info.get("accessViewStatus")),
        "epub_available": (access_info.get("epub") or {}).get("isAvailable"),
        "pdf_available": (access_info.get("pdf") or {}).get("isAvailable"),
        "localized": map_localized(volume_info),
        "trailers": [],
        "watch_links": [],
        "purchase_links": map_purchase_links(sale_info),
    }


async def fetch_json(client: httpx.AsyncClient, path: str, params: dict | None = None) -> dict:
    response = await client.get(path, params=params)
    response.raise_for_status()
    return response.json()


async def upsert_media_item(db, item_data: dict) -> None:
    now = datetime.now(UTC)

    await db.media_items.update_one(
        {
            "external_source": item_data["external_source"],
            "external_id": item_data["external_id"],
        },
        {
            "$set": {
                **item_data,
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            },
        },
        upsert=True,
    )


async def import_books(
    client: httpx.AsyncClient,
    db,
    query: str,
    pages: int,
    max_results_per_page: int,
) -> int:
    imported = 0
    start_index = 0

    for _ in range(pages):
        search_payload = await fetch_json(
            client,
            "/volumes",
            params={
                "q": query,
                "startIndex": start_index,
                "maxResults": max_results_per_page,
                "langRestrict": settings.GOOGLE_BOOKS_LANG,
                "country": settings.GOOGLE_BOOKS_COUNTRY,
                "printType": "books",
                "projection": "full",
                "key": settings.GOOGLE_BOOKS_API_KEY,
            },
        )

        items = search_payload.get("items", [])
        if not items:
            break

        for item in items:
            volume_id = item.get("id")
            if not volume_id:
                continue

            volume_payload = await fetch_json(
                client,
                f"/volumes/{volume_id}",
                params={
                    "projection": "full",
                    "country": settings.GOOGLE_BOOKS_COUNTRY,
                    "key": settings.GOOGLE_BOOKS_API_KEY,
                },
            )

            mapped = map_book_item(volume_payload)
            await upsert_media_item(db, mapped)
            imported += 1

        start_index += max_results_per_page

    return imported


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True, help='Наприклад: "intitle:dune"')
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--max-results", type=int, default=10)
    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 40:
        raise ValueError("Google Books maxResults must be between 1 and 40")

    client = AsyncMongoClient(settings.MONGODB_URL)

    try:
        db = client[settings.MONGODB_DB]

        async with httpx.AsyncClient(
            base_url=settings.GOOGLE_BOOKS_BASE_URL,
            timeout=30.0,
        ) as http_client:
            books_count = await import_books(
                http_client,
                db,
                query=args.query,
                pages=args.pages,
                max_results_per_page=args.max_results,
            )

        print(f"Imported/updated books: {books_count}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())