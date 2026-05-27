from app.repositories.admin_repository import (
    find_admin_comments,
    find_admin_forum_posts,
    find_admin_forum_threads,
    find_admin_items,
    get_admin_dashboard_counts,
)
from app.schemas.admin import (
    AdminCommentResponse,
    AdminCommentsListResponse,
    AdminDashboardStatsResponse,
    AdminForumPostResponse,
    AdminForumPostsListResponse,
    AdminForumThreadResponse,
    AdminForumThreadsListResponse,
    AdminItemResponse,
    AdminItemsListResponse,
)
from app.schemas.item import Category
from app.utils.avatar import resolve_avatar_id


def _optional_id(doc: dict, field_name: str) -> str | None:
    value = doc.get(field_name)
    return str(value) if value is not None else None


def _map_admin_item(doc: dict) -> AdminItemResponse:
    return AdminItemResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        category=doc["category"],
        year=doc["year"],
        genres=doc.get("genres", []),
        description=doc["description"],
        poster_url=doc.get("poster_url"),
        backdrop_url=doc.get("backdrop_url"),
        runtime=doc.get("runtime"),
        page_count=doc.get("page_count"),
        external_source=doc.get("external_source"),
        external_id=doc.get("external_id"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


def _map_admin_comment(doc: dict) -> AdminCommentResponse:
    item = doc.get("item") or {}

    return AdminCommentResponse(
        id=str(doc["_id"]),
        item_id=str(doc["item_id"]),
        item_title=item.get("title"),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=resolve_avatar_id(doc.get("author_avatar_id")),
        content=doc["text"],
        parent_comment_id=_optional_id(doc, "parent_comment_id"),
        reply_to_comment_id=_optional_id(doc, "reply_to_comment_id"),
        reply_to_username=doc.get("reply_to_username"),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


def _map_admin_forum_thread(doc: dict) -> AdminForumThreadResponse:
    return AdminForumThreadResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        content=doc["text"],
        category=doc["category_type"],
        custom_category=doc.get("custom_category"),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=resolve_avatar_id(doc.get("author_avatar_id")),
        posts_count=int(doc.get("replies_count", 0)),
        votes_count=int(doc.get("score", 0)),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


def _map_admin_forum_post(doc: dict) -> AdminForumPostResponse:
    thread = doc.get("thread") or {}

    return AdminForumPostResponse(
        id=str(doc["_id"]),
        thread_id=str(doc["thread_id"]),
        thread_title=thread.get("title"),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=resolve_avatar_id(doc.get("author_avatar_id")),
        content=doc["text"],
        parent_post_id=_optional_id(doc, "parent_post_id"),
        reply_to_post_id=_optional_id(doc, "reply_to_post_id"),
        reply_to_username=doc.get("reply_to_username"),
        votes_count=int(doc.get("score", 0)),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


async def get_admin_items_list(
    search: str | None = None,
    category: Category | None = None,
    limit: int = 20,
    skip: int = 0,
) -> AdminItemsListResponse:
    docs, total = await find_admin_items(
        search=search,
        category=category,
        limit=limit,
        skip=skip,
    )

    return AdminItemsListResponse(
        results=[_map_admin_item(doc) for doc in docs],
        total=total,
        limit=limit,
        skip=skip,
    )


async def get_admin_comments_list(
    search: str | None = None,
    item_id: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> AdminCommentsListResponse:
    docs, total = await find_admin_comments(
        search=search,
        item_id=item_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )

    return AdminCommentsListResponse(
        results=[_map_admin_comment(doc) for doc in docs],
        total=total,
        limit=limit,
        skip=skip,
    )


async def get_admin_forum_threads_list(
    search: str | None = None,
    category: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> AdminForumThreadsListResponse:
    docs, total = await find_admin_forum_threads(
        search=search,
        category=category,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )

    return AdminForumThreadsListResponse(
        results=[_map_admin_forum_thread(doc) for doc in docs],
        total=total,
        limit=limit,
        skip=skip,
    )


async def get_admin_forum_posts_list(
    search: str | None = None,
    thread_id: str | None = None,
    user_id: str | None = None,
    limit: int = 20,
    skip: int = 0,
) -> AdminForumPostsListResponse:
    docs, total = await find_admin_forum_posts(
        search=search,
        thread_id=thread_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )

    return AdminForumPostsListResponse(
        results=[_map_admin_forum_post(doc) for doc in docs],
        total=total,
        limit=limit,
        skip=skip,
    )


async def get_admin_dashboard_stats() -> AdminDashboardStatsResponse:
    counts = await get_admin_dashboard_counts()
    return AdminDashboardStatsResponse(**counts)