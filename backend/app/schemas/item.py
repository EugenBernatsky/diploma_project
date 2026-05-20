from typing import Literal

from pydantic import BaseModel, Field


Category = Literal["movie", "series", "book"]


class TrailerLink(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    site: str | None = None
    url: str = Field(min_length=1, max_length=1000)
    language: str | None = None


class WatchLink(BaseModel):
    provider_name: str = Field(min_length=1, max_length=300)
    provider_type: str | None = None
    region: str | None = None
    url: str = Field(min_length=1, max_length=1000)


class PurchaseLink(BaseModel):
    store_name: str = Field(min_length=1, max_length=300)
    region: str | None = None
    url: str = Field(min_length=1, max_length=1000)
    price: float | None = None
    currency: str | None = None


class LocalizedItemContent(BaseModel):
    title: str | None = None
    description: str | None = None
    tagline: str | None = None


class EpisodeShortInfo(BaseModel):
    name: str | None = None
    air_date: str | None = None
    episode_number: int | None = None
    season_number: int | None = None
    runtime: int | None = None
    overview: str | None = None
    still_url: str | None = None


class IndustryIdentifier(BaseModel):
    type: str
    identifier: str


class MediaItem(BaseModel):
    id: str
    title: str
    category: Category
    year: int
    genres: list[str]
    description: str

    poster_url: str | None = None
    backdrop_url: str | None = None

    external_source: str | None = None
    external_id: str | None = None

    original_title: str | None = None
    original_name: str | None = None
    original_language: str | None = None

    release_date: str | None = None
    first_air_date: str | None = None

    tagline: str | None = None
    content_status: str | None = None
    homepage: str | None = None

    production_countries: list[str] = Field(default_factory=list)

    tmdb_vote_average: float | None = None
    tmdb_vote_count: int | None = None

    runtime: int | None = None
    imdb_id: str | None = None

    episode_run_time: list[int] = Field(default_factory=list)
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    networks: list[str] = Field(default_factory=list)
    next_episode_to_air: EpisodeShortInfo | None = None
    last_episode_to_air: EpisodeShortInfo | None = None

    # Books
    subtitle: str | None = None
    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    published_date: str | None = None
    page_count: int | None = None
    industry_identifiers: list[IndustryIdentifier] = Field(default_factory=list)

    book_rating_average: float | None = None
    book_ratings_count: int | None = None

    preview_link: str | None = None
    info_link: str | None = None
    canonical_link: str | None = None
    web_reader_link: str | None = None

    saleability: str | None = None
    is_ebook: bool | None = None

    localized: dict[str, LocalizedItemContent] = Field(default_factory=dict)

    trailers: list[TrailerLink] = Field(default_factory=list)
    watch_links: list[WatchLink] = Field(default_factory=list)
    purchase_links: list[PurchaseLink] = Field(default_factory=list)

    viewability: str | None = None
    access_view_status: str | None = None
    epub_available: bool | None = None
    pdf_available: bool | None = None


class MediaItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    category: Category
    year: int = Field(ge=0, le=3000)
    genres: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1, max_length=5000)

    poster_url: str | None = None
    backdrop_url: str | None = None

    external_source: str | None = None
    external_id: str | None = None

    original_title: str | None = None
    original_name: str | None = None
    original_language: str | None = None

    release_date: str | None = None
    first_air_date: str | None = None

    tagline: str | None = None
    content_status: str | None = None
    homepage: str | None = None

    production_countries: list[str] = Field(default_factory=list)

    tmdb_vote_average: float | None = None
    tmdb_vote_count: int | None = None

    runtime: int | None = None
    imdb_id: str | None = None

    episode_run_time: list[int] = Field(default_factory=list)
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    networks: list[str] = Field(default_factory=list)
    next_episode_to_air: EpisodeShortInfo | None = None
    last_episode_to_air: EpisodeShortInfo | None = None

    # Books
    subtitle: str | None = None
    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    published_date: str | None = None
    page_count: int | None = None
    industry_identifiers: list[IndustryIdentifier] = Field(default_factory=list)

    book_rating_average: float | None = None
    book_ratings_count: int | None = None

    preview_link: str | None = None
    info_link: str | None = None
    canonical_link: str | None = None
    web_reader_link: str | None = None

    saleability: str | None = None
    is_ebook: bool | None = None

    localized: dict[str, LocalizedItemContent] = Field(default_factory=dict)

    trailers: list[TrailerLink] = Field(default_factory=list)
    watch_links: list[WatchLink] = Field(default_factory=list)
    purchase_links: list[PurchaseLink] = Field(default_factory=list)

    viewability: str | None = None
    access_view_status: str | None = None
    epub_available: bool | None = None
    pdf_available: bool | None = None


class MediaItemUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    category: Category
    year: int = Field(ge=0, le=3000)
    genres: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1, max_length=5000)

    poster_url: str | None = None
    backdrop_url: str | None = None

    external_source: str | None = None
    external_id: str | None = None

    original_title: str | None = None
    original_name: str | None = None
    original_language: str | None = None

    release_date: str | None = None
    first_air_date: str | None = None

    tagline: str | None = None
    content_status: str | None = None
    homepage: str | None = None

    production_countries: list[str] = Field(default_factory=list)

    tmdb_vote_average: float | None = None
    tmdb_vote_count: int | None = None

    runtime: int | None = None
    imdb_id: str | None = None

    episode_run_time: list[int] = Field(default_factory=list)
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    networks: list[str] = Field(default_factory=list)
    next_episode_to_air: EpisodeShortInfo | None = None
    last_episode_to_air: EpisodeShortInfo | None = None

    # Books
    subtitle: str | None = None
    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    published_date: str | None = None
    page_count: int | None = None
    industry_identifiers: list[IndustryIdentifier] = Field(default_factory=list)

    book_rating_average: float | None = None
    book_ratings_count: int | None = None

    preview_link: str | None = None
    info_link: str | None = None
    canonical_link: str | None = None
    web_reader_link: str | None = None

    saleability: str | None = None
    is_ebook: bool | None = None

    localized: dict[str, LocalizedItemContent] = Field(default_factory=dict)

    trailers: list[TrailerLink] = Field(default_factory=list)
    watch_links: list[WatchLink] = Field(default_factory=list)
    purchase_links: list[PurchaseLink] = Field(default_factory=list)

    viewability: str | None = None
    access_view_status: str | None = None
    epub_available: bool | None = None
    pdf_available: bool | None = None


class ItemActionResponse(BaseModel):
    message: str