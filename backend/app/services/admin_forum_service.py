from fastapi import HTTPException

from app.repositories.forum_posts_repository import (
    delete_post_tree,
    delete_posts_by_thread_id,
    find_post_by_id,
    find_post_tree_docs,
    find_posts_by_thread,
    find_recent_posts,
)
from app.repositories.forum_threads_repository import (
    decrement_thread_replies_count,
    delete_thread_by_id,
    find_thread_by_id,
    find_threads,
)
from app.repositories.forum_votes_repository import (
    delete_votes_for_target,
    delete_votes_for_targets,
)
from app.schemas.forum import ForumActionResponse, ForumPostBaseResponse, ForumThreadResponse
from app.schemas.user import UserPublic
from app.services.notifications_service import (
    notify_forum_post_deleted_by_admin,
    notify_forum_thread_deleted_by_admin,
)
from app.utils.avatar import resolve_avatar_id
from app.repositories.notifications_repository import (
    delete_notifications_by_post_ids,
    delete_notifications_by_thread_id,
)


def _get_optional_id_str(doc: dict, field_name: str) -> str | None:
    value = doc.get(field_name)
    return str(value) if value is not None else None


def _get_parent_post_id_str(doc: dict) -> str | None:
    return _get_optional_id_str(doc, "parent_post_id")


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


async def get_recent_threads_for_admin(limit: int = 100) -> list[ForumThreadResponse]:
    docs = await find_threads(limit=limit, sort_by="newest")
    return [_map_doc_to_thread_response(doc) for doc in docs]


async def get_recent_posts_for_admin(limit: int = 100) -> list[ForumPostBaseResponse]:
    docs = await find_recent_posts(limit=limit)
    return [_map_doc_to_post_base_response(doc) for doc in docs]


async def admin_delete_thread(current_admin: UserPublic, thread_id: str) -> ForumActionResponse:
    thread = await find_thread_by_id(thread_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread_owner_id = str(thread["user_id"])
    thread_title = thread["title"]

    post_docs = await find_posts_by_thread(thread_id, limit=5000)
    post_ids = [str(doc["_id"]) for doc in post_docs]

    deleted_thread = await delete_thread_by_id(thread_id)

    if not deleted_thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    await delete_posts_by_thread_id(thread_id)
    await delete_votes_for_target("thread", thread_id)
    await delete_votes_for_targets("post", post_ids)
    await delete_notifications_by_thread_id(thread_id)

    if thread_owner_id != current_admin.id:
        await notify_forum_thread_deleted_by_admin(
            recipient_user_id=thread_owner_id,
            thread_id=thread_id,
            thread_title=thread_title,
        )

    notified_users = {thread_owner_id, current_admin.id}

    for post_doc in post_docs:
        post_owner_id = str(post_doc["user_id"])

        if post_owner_id in notified_users:
            continue

        await notify_forum_post_deleted_by_admin(
            recipient_user_id=post_owner_id,
            thread_id=thread_id,
            thread_title=thread_title,
            post_id=str(post_doc["_id"]),
            reason="Пост було видалено разом із усією гілкою.",
        )
        notified_users.add(post_owner_id)

    return ForumActionResponse(message="Thread deleted by admin")


async def admin_delete_post(current_admin: UserPublic, post_id: str) -> ForumActionResponse:
    post = await find_post_by_id(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    thread = await find_thread_by_id(str(post["thread_id"]))
    thread_title = thread["title"] if thread is not None else "Без назви"

    post_tree_docs = await find_post_tree_docs(post_id)
    post_tree_ids = [str(doc["_id"]) for doc in post_tree_docs]

    deleted_count = await delete_post_tree(post_id)

    if deleted_count <= 0:
        raise HTTPException(status_code=404, detail="Post not found")

    await decrement_thread_replies_count(str(post["thread_id"]), amount=deleted_count)
    await delete_votes_for_targets("post", post_tree_ids)
    await delete_notifications_by_post_ids(post_tree_ids)

    notified_users = {current_admin.id}

    for post_doc in post_tree_docs:
        post_owner_id = str(post_doc["user_id"])

        if post_owner_id in notified_users:
            continue

        await notify_forum_post_deleted_by_admin(
            recipient_user_id=post_owner_id,
            thread_id=str(post["thread_id"]),
            thread_title=thread_title,
            post_id=str(post_doc["_id"]),
        )
        notified_users.add(post_owner_id)

    return ForumActionResponse(message="Post deleted by admin")