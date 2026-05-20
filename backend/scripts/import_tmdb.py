import argparse
import asyncio
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import httpx
from pymongo import AsyncMongoClient

from app.core.config import settings

MediaKind = Literal["movie", "tv"]
DEBUG_DIR = Path("debug_payloads")
DEFAULT_TIMEOUT = 30.0
DEFAULT_CONCURRENCY = 6
DEFAULT_RETRIES = 4


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def dump_payload(filename: str, payload: dict[str, Any]) -> None:
    DEBUG_DIR.mkdir(exist_ok=True)
    filepath = DEBUG_DIR / filename
    filepath.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[debug] Saved payload: {filepath.resolve()}")


def build_image_url(file_path: str | None, size: str) -> str | None:
    if not file_path:
        return None
    return f"{settings.TMDB_IMAGE_BASE_URL}/{size}{file_path}"


def extract_year(date_str: str | None) -> int:
    if not date_str or len(date_str) < 4:
        return 0
    try:
        return int(date_str[:4])
    except ValueError:
        return 0


def unique_non_empty(values: Iterable[str | None]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def map_genres(details: dict[str, Any]) -> list[str]:
    return unique_non_empty(genre.get("name") for genre in details.get("genres", []))


def map_trailers(videos_payload: dict[str, Any]) -> list[dict[str, Any]]:
    results = videos_payload.get("results", [])
    trailers: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for video in results:
        site = video.get("site")
        key = video.get("key")
        video_type = video.get("type")

        if not key or site not in {"YouTube", "Vimeo"}:
            continue
        if video_type not in {"Trailer", "Teaser"}:
            continue

        if site == "YouTube":
            url = f"https://www.youtube.com/watch?v={key}"
        else:
            url = f"https://vimeo.com/{key}"

        if url in seen_urls:
            continue
        seen_urls.add(url)

        trailers.append(
            {
                "name": normalize_text(video.get("name")) or "Trailer",
                "site": site,
                "url": url,
                "language": normalize_text(video.get("iso_639_1")),
            }
        )

    return trailers[:3]


def map_watch_links(watch_payload: dict[str, Any]) -> list[dict[str, Any]]:
    region_data = watch_payload.get("results", {}).get(settings.TMDB_REGION, {})
    provider_page = normalize_text(region_data.get("link"))
    if not region_data or not provider_page:
        return []

    links: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for provider_type in ["flatrate", "buy", "rent", "free", "ads"]:
        providers = region_data.get(provider_type, [])
        for provider in providers:
            provider_name = normalize_text(provider.get("provider_name"))
            key = (provider_name or "", provider_type)
            if not provider_name or key in seen:
                continue
            seen.add(key)
            links.append(
                {
                    "provider_name": provider_name,
                    "provider_type": provider_type,
                    "region": settings.TMDB_REGION,
                    "url": provider_page,
                }
            )

    return links


def map_production_countries(details: dict[str, Any]) -> list[str]:
    return unique_non_empty(
        country.get("name") for country in details.get("production_countries", [])
    )


def map_networks(details: dict[str, Any]) -> list[str]:
    return unique_non_empty(network.get("name") for network in details.get("networks", []))


def map_episode_short_info(episode: dict[str, Any] | None) -> dict[str, Any] | None:
    if not episode:
        return None

    return {
        "name": normalize_text(episode.get("name")),
        "air_date": normalize_text(episode.get("air_date")),
        "episode_number": episode.get("episode_number"),
        "season_number": episode.get("season_number"),
        "runtime": episode.get("runtime"),
        "overview": normalize_text(episode.get("overview")),
        "still_url": build_image_url(
            episode.get("still_path"),
            settings.TMDB_BACKDROP_SIZE,
        ),
    }


def map_localized(details: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        settings.TMDB_LANGUAGE: {
            "title": normalize_text(details.get("title") or details.get("name")),
            "description": normalize_text(details.get("overview")),
            "tagline": normalize_text(details.get("tagline")),
        }
    }


def map_movie_item(details: dict[str, Any], videos: dict[str, Any], watch_providers: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": normalize_text(details.get("title")) or "Untitled",
        "category": "movie",
        "year": extract_year(details.get("release_date")),
        "genres": map_genres(details),
        "description": normalize_text(details.get("overview")) or "No description available.",
        "poster_url": build_image_url(details.get("poster_path"), settings.TMDB_POSTER_SIZE),
        "backdrop_url": build_image_url(details.get("backdrop_path"), settings.TMDB_BACKDROP_SIZE),
        "external_source": "tmdb",
        "external_id": str(details["id"]),
        "original_title": normalize_text(details.get("original_title")),
        "original_name": None,
        "original_language": normalize_text(details.get("original_language")),
        "release_date": normalize_text(details.get("release_date")),
        "first_air_date": None,
        "tagline": normalize_text(details.get("tagline")),
        "content_status": normalize_text(details.get("status")),
        "homepage": normalize_text(details.get("homepage")),
        "production_countries": map_production_countries(details),
        "tmdb_vote_average": details.get("vote_average"),
        "tmdb_vote_count": details.get("vote_count"),
        "runtime": details.get("runtime"),
        "imdb_id": normalize_text(details.get("imdb_id")),
        "episode_run_time": [],
        "number_of_seasons": None,
        "number_of_episodes": None,
        "networks": [],
        "next_episode_to_air": None,
        "last_episode_to_air": None,
        "localized": map_localized(details),
        "trailers": map_trailers(videos),
        "watch_links": map_watch_links(watch_providers),
        "purchase_links": [],
    }


def map_tv_item(details: dict[str, Any], videos: dict[str, Any], watch_providers: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": normalize_text(details.get("name")) or "Untitled",
        "category": "series",
        "year": extract_year(details.get("first_air_date")),
        "genres": map_genres(details),
        "description": normalize_text(details.get("overview")) or "No description available.",
        "poster_url": build_image_url(details.get("poster_path"), settings.TMDB_POSTER_SIZE),
        "backdrop_url": build_image_url(details.get("backdrop_path"), settings.TMDB_BACKDROP_SIZE),
        "external_source": "tmdb",
        "external_id": str(details["id"]),
        "original_title": None,
        "original_name": normalize_text(details.get("original_name")),
        "original_language": normalize_text(details.get("original_language")),
        "release_date": None,
        "first_air_date": normalize_text(details.get("first_air_date")),
        "tagline": normalize_text(details.get("tagline")),
        "content_status": normalize_text(details.get("status")),
        "homepage": normalize_text(details.get("homepage")),
        "production_countries": map_production_countries(details),
        "tmdb_vote_average": details.get("vote_average"),
        "tmdb_vote_count": details.get("vote_count"),
        "runtime": None,
        "imdb_id": None,
        "episode_run_time": details.get("episode_run_time", []),
        "number_of_seasons": details.get("number_of_seasons"),
        "number_of_episodes": details.get("number_of_episodes"),
        "networks": map_networks(details),
        "next_episode_to_air": map_episode_short_info(details.get("next_episode_to_air")),
        "last_episode_to_air": map_episode_short_info(details.get("last_episode_to_air")),
        "localized": map_localized(details),
        "trailers": map_trailers(videos),
        "watch_links": map_watch_links(watch_providers),
        "purchase_links": [],
    }


class TmdbImporter:
    def __init__(
        self,
        client: httpx.AsyncClient,
        db,
        *,
        retries: int,
        concurrency: int,
        save_debug_payloads: bool,
        skip_existing: bool,
    ) -> None:
        self.client = client
        self.db = db
        self.retries = retries
        self.semaphore = asyncio.Semaphore(concurrency)
        self.save_debug_payloads = save_debug_payloads
        self.skip_existing = skip_existing
        self._debug_dumped_for: set[str] = set()
        self.stats = {
            "inserted": 0,
            "updated": 0,
            "unchanged": 0,
            "skipped_existing": 0,
            "failed": 0,
        }

    async def fetch_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        last_error: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                response = await self.client.get(path, params=params)
                response.raise_for_status()
                return response.json()
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                last_error = exc
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                should_retry = (
                    status_code in {429, 500, 502, 503, 504}
                    or isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))
                )
                if attempt >= self.retries or not should_retry:
                    raise

                delay = min(2 ** (attempt - 1), 8)
                print(
                    f"[retry] {path} failed on attempt {attempt}/{self.retries}"
                    f" (status={status_code}). Sleeping {delay}s..."
                )
                await asyncio.sleep(delay)

        assert last_error is not None
        raise last_error

    async def upsert_media_item(self, item_data: dict[str, Any]) -> str:
        now = datetime.now(UTC)
        result = await self.db.media_items.update_one(
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

        if result.upserted_id is not None:
            self.stats["inserted"] += 1
            return "inserted"
        if result.modified_count > 0:
            self.stats["updated"] += 1
            return "updated"

        self.stats["unchanged"] += 1
        return "unchanged"

    async def skip_existing_ids(self, tmdb_ids: list[int]) -> set[int]:
        if not self.skip_existing or not tmdb_ids:
            return set()

        cursor = self.db.media_items.find(
            {
                "external_source": "tmdb",
                "external_id": {"$in": [str(tmdb_id) for tmdb_id in tmdb_ids]},
            },
            {"external_id": 1},
        )
        existing = await cursor.to_list(length=len(tmdb_ids))
        return {int(doc["external_id"]) for doc in existing if doc.get("external_id")}

    async def fetch_media_payloads(self, kind: MediaKind, tmdb_id: int) -> tuple[dict[str, Any], dict[str, Any]]:
        details_task = self.fetch_json(
            f"/{kind}/{tmdb_id}",
            params={
                "language": settings.TMDB_LANGUAGE,
                "append_to_response": "videos",
            },
        )
        watch_task = self.fetch_json(f"/{kind}/{tmdb_id}/watch/providers")
        details, watch_providers = await asyncio.gather(details_task, watch_task)
        videos = details.get("videos") or {}
        return details, videos if isinstance(videos, dict) else {}, watch_providers

    async def process_item(self, kind: MediaKind, tmdb_id: int) -> None:
        async with self.semaphore:
            try:
                details, videos, watch_providers = await self.fetch_media_payloads(kind, tmdb_id)

                if self.save_debug_payloads and kind not in self._debug_dumped_for:
                    dump_payload(f"{kind}_{tmdb_id}_details.json", details)
                    dump_payload(f"{kind}_{tmdb_id}_watch_providers.json", watch_providers)
                    self._debug_dumped_for.add(kind)

                if kind == "movie":
                    mapped = map_movie_item(details, videos, watch_providers)
                else:
                    mapped = map_tv_item(details, videos, watch_providers)

                outcome = await self.upsert_media_item(mapped)
                print(f"[{kind}] {tmdb_id} -> {mapped['title']} ({outcome})")
            except Exception as exc:
                self.stats["failed"] += 1
                print(f"[error] {kind} {tmdb_id}: {exc}")

    async def import_kind(self, kind: MediaKind, pages: int) -> None:
        if pages <= 0:
            return

        discover_path = "/discover/movie" if kind == "movie" else "/discover/tv"

        for page in range(1, pages + 1):
            discover_payload = await self.fetch_json(
                discover_path,
                params={
                    "page": page,
                    "sort_by": "popularity.desc",
                    "include_adult": "false",
                    "language": settings.TMDB_LANGUAGE,
                },
            )

            if self.save_debug_payloads and page == 1:
                dump_payload(f"{kind}_discover_page_1.json", discover_payload)

            results = discover_payload.get("results", [])
            if not results:
                print(f"[{kind}] page {page}: no results, stopping")
                break

            tmdb_ids = [item["id"] for item in results if item.get("id") is not None]
            existing_ids = await self.skip_existing_ids(tmdb_ids)
            if existing_ids:
                self.stats["skipped_existing"] += len(existing_ids)

            ids_to_process = [tmdb_id for tmdb_id in tmdb_ids if tmdb_id not in existing_ids]
            print(
                f"[{kind}] page {page}: total={len(tmdb_ids)}, "
                f"skip_existing={len(existing_ids)}, process={len(ids_to_process)}"
            )

            tasks = [self.process_item(kind, tmdb_id) for tmdb_id in ids_to_process]
            if tasks:
                await asyncio.gather(*tasks)

    async def import_all(self, movies_pages: int, series_pages: int) -> None:
        await self.import_kind("movie", movies_pages)
        await self.import_kind("tv", series_pages)


async def ensure_external_index(db) -> None:
    existing_indexes = await db.media_items.index_information()
    target_keys = [("external_source", 1), ("external_id", 1)]

    for index_name, index_info in existing_indexes.items():
        if index_info.get("key") == target_keys and index_info.get("unique") is True:
            print(f"[info] External unique index already exists: {index_name}")
            return

    old_name = "external_source_1_external_id_1"
    old_index = existing_indexes.get(old_name)
    if old_index and old_index.get("key") == target_keys and not old_index.get("unique"):
        print(
            "[warn] Found old non-unique index external_source_1_external_id_1. "
            "Dropping it before import..."
        )
        await db.media_items.drop_index(old_name)

    await db.media_items.create_index(
        target_keys,
        unique=True,
    )
    print("[info] Created unique index on external_source + external_id")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--movies-pages", type=int, default=1)
    parser.add_argument("--series-pages", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--save-debug-payloads", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    headers = {
        "Authorization": f"Bearer {settings.TMDB_API_READ_TOKEN}",
        "accept": "application/json",
    }

    client = AsyncMongoClient(settings.MONGODB_URL)

    try:
        db = client[settings.MONGODB_DB]
        await ensure_external_index(db)

        limits = httpx.Limits(max_connections=args.concurrency + 2, max_keepalive_connections=args.concurrency)
        async with httpx.AsyncClient(
            base_url=settings.TMDB_BASE_URL,
            headers=headers,
            timeout=args.timeout,
            limits=limits,
        ) as http_client:
            importer = TmdbImporter(
                http_client,
                db,
                retries=args.retries,
                concurrency=args.concurrency,
                save_debug_payloads=args.save_debug_payloads,
                skip_existing=args.skip_existing,
            )
            await importer.import_all(args.movies_pages, args.series_pages)

        print("\n=== TMDB import summary ===")
        for key, value in importer.stats.items():
            print(f"{key}: {value}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
