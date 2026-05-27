from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.forum_posts_repository import (
    delete_post_tree,
    delete_posts_by_thread_id,
    find_post_by_id,
    find_post_ids_by_thread,
    find_post_tree_ids,
    find_posts_by_thread,
    insert_post,
    update_post_text,
)
from app.repositories.forum_threads_repository import (
    decrement_thread_replies_count,
    delete_thread_by_id,
    find_thread_by_id,
    find_threads,
    increment_thread_replies_count,
    insert_thread,
    update_thread_content,
)
from app.repositories.forum_votes_repository import (
    delete_votes_for_target,
    delete_votes_for_targets,
)
from app.repositories.users_repository import find_user_by_id
from app.schemas.forum import (
    ForumActionResponse,
    ForumPostBaseResponse,
    ForumPostCreate,
    ForumPostReplyResponse,
    ForumPostResponse,
    ForumPostUpdate,
    ForumThreadCreate,
    ForumThreadResponse,
    ForumThreadUpdate,
)
from app.schemas.user import UserPublic
from app.services.notifications_service import (
    notify_reply_to_forum_post,
    notify_reply_to_forum_thread,
)
from app.utils.avatar import resolve_avatar_id
from app.repositories.notifications_repository import (
    delete_notifications_by_post_ids,
    delete_notifications_by_thread_id,
)


def _normalize_forum_text(text: str) -> str:
    normalized = text.strip()

    if not normalized:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    return normalized


def _normalize_forum_title(title: str) -> str:
    normalized = title.strip()

    if not normalized:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    return normalized

def _normalize_custom_category(custom_category: str | None) -> str | None:
    if custom_category is None:
        return None

    normalized = custom_category.strip()
    return normalized or None

def _get_author_avatar_id(doc: dict) -> str:
    return resolve_avatar_id(doc.get("author_avatar_id"))


def _map_doc_to_thread_response(doc: dict) -> ForumThreadResponse:
    created_at = doc["created_at"]
    updated_at = doc["updated_at"]

    return ForumThreadResponse(
        id=str(doc["_id"]),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=_get_author_avatar_id(doc),
        title=doc["title"],
        text=doc["text"],
        category_type=doc.get("category_type", "custom"),
        custom_category=doc.get("custom_category"),
        score=doc.get("score", 0),
        replies_count=doc["replies_count"],
        created_at=created_at,
        updated_at=updated_at,
        last_activity_at=doc["last_activity_at"],
        edited=updated_at > created_at,
    )


def _get_optional_id_str(doc: dict, field_name: str) -> str | None:
    value = doc.get(field_name)
    return str(value) if value is not None else None


def _get_parent_post_id_str(doc: dict) -> str | None:
    return _get_optional_id_str(doc, "parent_post_id")


def _map_doc_to_post_base_response(doc: dict) -> ForumPostBaseResponse:
    created_at = doc["created_at"]
    updated_at = doc["updated_at"]

    return ForumPostBaseResponse(
        id=str(doc["_id"]),
        thread_id=str(doc["thread_id"]),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=_get_author_avatar_id(doc),
        text=doc["text"],
        score=doc.get("score", 0),
        parent_post_id=_get_parent_post_id_str(doc),

        # Нові поля для reply-to-reply.
        reply_to_post_id=_get_optional_id_str(doc, "reply_to_post_id"),
        reply_to_user_id=_get_optional_id_str(doc, "reply_to_user_id"),
        reply_to_username=doc.get("reply_to_username"),

        created_at=created_at,
        updated_at=updated_at,
        edited=updated_at > created_at,
    )


def _map_doc_to_post_reply_response(doc: dict) -> ForumPostReplyResponse:
    base = _map_doc_to_post_base_response(doc)
    return ForumPostReplyResponse(**base.model_dump())


def _map_doc_to_post_response(doc: dict, replies: list[dict]) -> ForumPostResponse:
    base = _map_doc_to_post_base_response(doc)
    return ForumPostResponse(
        **base.model_dump(),
        replies=[_map_doc_to_post_reply_response(reply) for reply in replies],
    )


async def get_threads_list(
    limit: int = 100,
    sort_by: str = "activity",
    category_type: str | None = None,
    custom_category: str | None = None,
) -> list[ForumThreadResponse]:
    docs = await find_threads(
        limit=limit,
        sort_by=sort_by,
        category_type=category_type,
        custom_category=custom_category,
    )
    return [_map_doc_to_thread_response(doc) for doc in docs]


async def get_thread(thread_id: str) -> ForumThreadResponse:
    doc = await find_thread_by_id(thread_id)

    if doc is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    return _map_doc_to_thread_response(doc)


async def create_thread_forum(
    current_user: UserPublic,
    payload: ForumThreadCreate,
) -> ForumThreadResponse:
    user_doc = await find_user_by_id(current_user.id)
    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(UTC)

    created_thread = await insert_thread(
        user_id=current_user.id,
        author_username=current_user.username,
        author_avatar_id=resolve_avatar_id(user_doc.get("avatar_id")),
        title=_normalize_forum_title(payload.title),
        text=_normalize_forum_text(payload.text),
        category_type=payload.category_type,
        custom_category=_normalize_custom_category(payload.custom_category),
        created_at=now,
        updated_at=now,
        last_activity_at=now,
    )

    return _map_doc_to_thread_response(created_thread)


async def edit_own_thread(
    current_user: UserPublic,
    thread_id: str,
    payload: ForumThreadUpdate,
) -> ForumThreadResponse:
    thread = await find_thread_by_id(thread_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    if str(thread["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own threads")

    updated_thread = await update_thread_content(
        thread_id=thread_id,
        title=_normalize_forum_title(payload.title),
        text=_normalize_forum_text(payload.text),
        category_type=payload.category_type,
        custom_category=_normalize_custom_category(payload.custom_category),
        updated_at=datetime.now(UTC),
    )

    if updated_thread is None:
        raise RuntimeError("Failed to fetch updated thread")

    return _map_doc_to_thread_response(updated_thread)


async def delete_own_thread(
    current_user: UserPublic,
    thread_id: str,
) -> ForumActionResponse:
    thread = await find_thread_by_id(thread_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    if str(thread["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can delete only your own threads")

    post_ids = await find_post_ids_by_thread(thread_id)

    deleted_thread = await delete_thread_by_id(thread_id)

    if not deleted_thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    await delete_posts_by_thread_id(thread_id)
    await delete_votes_for_target("thread", thread_id)
    await delete_votes_for_targets("post", post_ids)
    await delete_notifications_by_thread_id(thread_id)

    return ForumActionResponse(message="Thread deleted successfully")


async def get_thread_posts(
    thread_id: str,
    limit: int = 200,
) -> list[ForumPostResponse]:
    thread = await find_thread_by_id(thread_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    docs = await find_posts_by_thread(thread_id, limit=limit)

    top_level_posts: list[dict] = []
    replies_by_parent_id: dict[str, list[dict]] = {}

    for doc in docs:
        parent_post_id = doc.get("parent_post_id")

        if parent_post_id is None:
            top_level_posts.append(doc)
            continue

        parent_id_str = str(parent_post_id)
        replies_by_parent_id.setdefault(parent_id_str, []).append(doc)

    return [
        _map_doc_to_post_response(
            doc,
            replies_by_parent_id.get(str(doc["_id"]), []),
        )
        for doc in top_level_posts
    ]


async def create_thread_post(
    current_user: UserPublic,
    thread_id: str,
    payload: ForumPostCreate,
) -> ForumPostBaseResponse:
    thread = await find_thread_by_id(thread_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    target_post_id = payload.reply_to_post_id or payload.parent_post_id

    actual_parent_post_id: str | None = None
    reply_to_post_id: str | None = None
    reply_to_user_id: str | None = None
    reply_to_username: str | None = None

    if target_post_id is not None:
        target_post = await find_post_by_id(target_post_id)

        if target_post is None:
            raise HTTPException(status_code=404, detail="Target post not found")

        if str(target_post["thread_id"]) != thread_id:
            raise HTTPException(status_code=400, detail="Target post belongs to another thread")

        target_parent_id = target_post.get("parent_post_id")
        actual_parent_post_id = (
            str(target_parent_id)
            if target_parent_id is not None
            else str(target_post["_id"])
        )

        reply_to_post_id = str(target_post["_id"])
        reply_to_user_id = str(target_post["user_id"])
        reply_to_username = target_post["author_username"]

    user_doc = await find_user_by_id(current_user.id)
    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(UTC)

    created_post = await insert_post(
        user_id=current_user.id,
        thread_id=thread_id,
        author_username=current_user.username,
        author_avatar_id=resolve_avatar_id(user_doc.get("avatar_id")),
        text=_normalize_forum_text(payload.text),

        parent_post_id=actual_parent_post_id,

        reply_to_post_id=reply_to_post_id,
        reply_to_user_id=reply_to_user_id,
        reply_to_username=reply_to_username,

        created_at=now,
        updated_at=now,
    )

    await increment_thread_replies_count(thread_id, last_activity_at=now)

    notified_user_ids: set[str] = set()
    thread_owner_id = str(thread["user_id"])

    if reply_to_user_id is not None and reply_to_user_id != current_user.id:
        await notify_reply_to_forum_post(
            recipient_user_id=reply_to_user_id,
            replier_username=current_user.username,
            thread_id=thread_id,
            thread_title=thread["title"],
            post_id=str(created_post["_id"]),
        )
        notified_user_ids.add(reply_to_user_id)

    if thread_owner_id != current_user.id and thread_owner_id not in notified_user_ids:
        await notify_reply_to_forum_thread(
            recipient_user_id=thread_owner_id,
            replier_username=current_user.username,
            thread_id=thread_id,
            thread_title=thread["title"],
            post_id=str(created_post["_id"]),
        )

    return _map_doc_to_post_base_response(created_post)


async def edit_own_post(
    current_user: UserPublic,
    post_id: str,
    payload: ForumPostUpdate,
) -> ForumPostBaseResponse:
    post = await find_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if str(post["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own posts")

    updated_post = await update_post_text(
        post_id=post_id,
        text=_normalize_forum_text(payload.text),
        updated_at=datetime.now(UTC),
    )

    if updated_post is None:
        raise RuntimeError("Failed to fetch updated post")

    return _map_doc_to_post_base_response(updated_post)


async def delete_own_post(
    current_user: UserPublic,
    post_id: str,
) -> ForumActionResponse:
    post = await find_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if str(post["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can delete only your own posts")

    post_tree_ids = await find_post_tree_ids(post_id)
    deleted_count = await delete_post_tree(post_id)

    if deleted_count <= 0:
        raise HTTPException(status_code=404, detail="Post not found")

    await decrement_thread_replies_count(str(post["thread_id"]), amount=deleted_count)
    await delete_votes_for_targets("post", post_tree_ids)
    await delete_notifications_by_post_ids(post_tree_ids)

    return ForumActionResponse(message="Post deleted successfully")