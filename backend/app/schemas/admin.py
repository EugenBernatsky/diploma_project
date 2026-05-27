from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.item import Category


ForumCategoryType = Literal["movie", "series", "book", "custom"]


class AdminItemResponse(BaseModel):
    id: str
    title: str
    category: Category
    year: int
    genres: list[str] = Field(default_factory=list)
    description: str

    poster_url: str | None = None
    backdrop_url: str | None = None

    runtime: int | None = None
    page_count: int | None = None

    external_source: str | None = None
    external_id: str | None = None

    created_at: datetime
    updated_at: datetime | None = None


class AdminItemsListResponse(BaseModel):
    results: list[AdminItemResponse]
    total: int
    limit: int
    skip: int


class AdminCommentResponse(BaseModel):
    id: str
    item_id: str
    item_title: str | None = None

    user_id: str
    author_username: str
    author_avatar_id: str | None = None

    content: str

    parent_comment_id: str | None = None
    reply_to_comment_id: str | None = None
    reply_to_username: str | None = None

    created_at: datetime
    updated_at: datetime | None = None


class AdminCommentsListResponse(BaseModel):
    results: list[AdminCommentResponse]
    total: int
    limit: int
    skip: int


class AdminForumThreadResponse(BaseModel):
    id: str
    title: str
    content: str

    category: ForumCategoryType
    custom_category: str | None = None

    user_id: str
    author_username: str
    author_avatar_id: str | None = None

    posts_count: int = 0
    votes_count: int = 0

    created_at: datetime
    updated_at: datetime | None = None


class AdminForumThreadsListResponse(BaseModel):
    results: list[AdminForumThreadResponse]
    total: int
    limit: int
    skip: int


class AdminForumPostResponse(BaseModel):
    id: str
    thread_id: str
    thread_title: str | None = None

    user_id: str
    author_username: str
    author_avatar_id: str | None = None

    content: str

    parent_post_id: str | None = None
    reply_to_post_id: str | None = None
    reply_to_username: str | None = None

    votes_count: int = 0

    created_at: datetime
    updated_at: datetime | None = None


class AdminForumPostsListResponse(BaseModel):
    results: list[AdminForumPostResponse]
    total: int
    limit: int
    skip: int


class AdminDashboardStatsResponse(BaseModel):
    users_count: int
    items_count: int
    comments_count: int
    forum_threads_count: int
    forum_posts_count: int
    unread_notifications_count: int