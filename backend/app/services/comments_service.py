from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.comments_repository import (
    delete_comment_tree,
    find_comment_by_id,
    find_comments_by_item,
    find_recent_comments,
    insert_comment,
    update_comment_text,
)
from app.repositories.items_repository import find_item_by_id
from app.repositories.users_repository import find_user_by_id
from app.schemas.comment import (
    CommentActionResponse,
    CommentBaseResponse,
    CommentCreate,
    CommentReplyResponse,
    CommentResponse,
    CommentUpdate,
)
from app.schemas.user import UserPublic
from app.services.notifications_service import (
    notify_comment_deleted_by_admin,
    notify_reply_to_comment,
)
from app.utils.avatar import resolve_avatar_id


def _get_optional_id_str(doc: dict, field_name: str) -> str | None:
    value = doc.get(field_name)
    return str(value) if value is not None else None


def _get_parent_comment_id_str(doc: dict) -> str | None:
    return _get_optional_id_str(doc, "parent_comment_id")

def _get_author_avatar_id(doc: dict) -> str:
    return resolve_avatar_id(doc.get("author_avatar_id"))


def _map_doc_to_comment_base_response(doc: dict) -> CommentBaseResponse:
    created_at = doc["created_at"]
    updated_at = doc["updated_at"]

    return CommentBaseResponse(
        id=str(doc["_id"]),
        item_id=str(doc["item_id"]),
        user_id=str(doc["user_id"]),
        author_username=doc["author_username"],
        author_avatar_id=_get_author_avatar_id(doc),
        text=doc["text"],
        parent_comment_id=_get_parent_comment_id_str(doc),

        # Нові поля для reply-to-reply.
        reply_to_comment_id=_get_optional_id_str(doc, "reply_to_comment_id"),
        reply_to_user_id=_get_optional_id_str(doc, "reply_to_user_id"),
        reply_to_username=doc.get("reply_to_username"),

        created_at=created_at,
        updated_at=updated_at,
        edited=updated_at > created_at,
    )


def _map_doc_to_comment_reply_response(doc: dict) -> CommentReplyResponse:
    base = _map_doc_to_comment_base_response(doc)
    return CommentReplyResponse(**base.model_dump())


def _map_doc_to_comment_response(doc: dict, replies: list[dict]) -> CommentResponse:
    base = _map_doc_to_comment_base_response(doc)
    return CommentResponse(
        **base.model_dump(),
        replies=[_map_doc_to_comment_reply_response(reply) for reply in replies],
    )


def _normalize_comment_text(text: str) -> str:
    normalized = text.strip()

    if not normalized:
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")

    return normalized


async def get_comments_for_item(item_id: str, limit: int = 100) -> list[CommentResponse]:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    docs = await find_comments_by_item(item_id, limit=limit)

    top_level_comments: list[dict] = []
    replies_by_parent_id: dict[str, list[dict]] = {}

    for doc in docs:
        parent_comment_id = doc.get("parent_comment_id")

        if parent_comment_id is None:
            top_level_comments.append(doc)
            continue

        parent_id_str = str(parent_comment_id)
        replies_by_parent_id.setdefault(parent_id_str, []).append(doc)

    return [
        _map_doc_to_comment_response(
            doc,
            replies_by_parent_id.get(str(doc["_id"]), []),
        )
        for doc in top_level_comments
    ]


async def create_comment_for_item(
    current_user: UserPublic,
    item_id: str,
    payload: CommentCreate,
) -> CommentBaseResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Новий фронт має надсилати reply_to_comment_id.
    # Старий фронт може ще надсилати parent_comment_id.
    # В обох випадках це ID коментаря, на який користувач натиснув Reply.
    target_comment_id = payload.reply_to_comment_id or payload.parent_comment_id

    actual_parent_comment_id: str | None = None
    reply_to_comment_id: str | None = None
    reply_to_user_id: str | None = None
    reply_to_username: str | None = None

    if target_comment_id is not None:
        target_comment = await find_comment_by_id(target_comment_id)

        if target_comment is None:
            raise HTTPException(status_code=404, detail="Target comment not found")

        if str(target_comment["item_id"]) != item_id:
            raise HTTPException(status_code=400, detail="Target comment belongs to another item")

        # Головна логіка:
        #
        # 1. Якщо відповідаємо на top-level comment:
        #    parent_comment_id = ID цього top-level comment
        #
        # 2. Якщо відповідаємо на reply:
        #    parent_comment_id = ID головного top-level comment
        #
        # Так ми дозволяємо reply-to-reply, але не створюємо глибоке дерево.
        target_parent_id = target_comment.get("parent_comment_id")
        actual_parent_comment_id = (
            str(target_parent_id)
            if target_parent_id is not None
            else str(target_comment["_id"])
        )

        # А тут зберігаємо конкретного адресата відповіді.
        reply_to_comment_id = str(target_comment["_id"])
        reply_to_user_id = str(target_comment["user_id"])
        reply_to_username = target_comment["author_username"]

    user_doc = await find_user_by_id(current_user.id)
    if user_doc is None:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(UTC)

    created_comment = await insert_comment(
        user_id=current_user.id,
        item_id=item_id,
        author_username=current_user.username,
        author_avatar_id=resolve_avatar_id(user_doc.get("avatar_id")),
        text=_normalize_comment_text(payload.text),

        # Це ID головного коментаря для групування.
        parent_comment_id=actual_parent_comment_id,

        # Це конкретний коментар, на який відповіли.
        reply_to_comment_id=reply_to_comment_id,
        reply_to_user_id=reply_to_user_id,
        reply_to_username=reply_to_username,

        created_at=now,
        updated_at=now,
    )

    # Notification тепер іде саме тому, кому відповіли,
    # а не обов'язково автору головного коментаря.
    if reply_to_user_id is not None and reply_to_user_id != current_user.id:
        await notify_reply_to_comment(
            recipient_user_id=reply_to_user_id,
            replier_username=current_user.username,
            item_id=item_id,
            item_title=item["title"],
            reply_comment_id=str(created_comment["_id"]),
        )

    return _map_doc_to_comment_base_response(created_comment)


async def edit_own_comment(
    current_user: UserPublic,
    comment_id: str,
    payload: CommentUpdate,
) -> CommentBaseResponse:
    comment = await find_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if str(comment["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own comments")

    updated_comment = await update_comment_text(
        comment_id=comment_id,
        text=_normalize_comment_text(payload.text),
        updated_at=datetime.now(UTC),
    )

    if updated_comment is None:
        raise RuntimeError("Failed to fetch updated comment")

    return _map_doc_to_comment_base_response(updated_comment)


async def delete_own_comment(
    current_user: UserPublic,
    comment_id: str,
) -> CommentActionResponse:
    comment = await find_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if str(comment["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You can delete only your own comments")

    deleted = await delete_comment_tree(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")

    return CommentActionResponse(message="Comment deleted successfully")


async def get_recent_comments_for_admin(limit: int = 100) -> list[CommentBaseResponse]:
    docs = await find_recent_comments(limit=limit)
    return [_map_doc_to_comment_base_response(doc) for doc in docs]


async def admin_delete_comment(
    current_admin: UserPublic,
    comment_id: str,
) -> CommentActionResponse:
    comment = await find_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment_owner_id = str(comment["user_id"])
    item_id = str(comment["item_id"])

    item = await find_item_by_id(item_id)
    item_title = item["title"] if item is not None else None

    deleted = await delete_comment_tree(comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment_owner_id != current_admin.id:
        await notify_comment_deleted_by_admin(
            recipient_user_id=comment_owner_id,
            item_id=item_id,
            item_title=item_title,
            deleted_comment_id=comment_id,
        )

    return CommentActionResponse(message="Comment deleted by admin")