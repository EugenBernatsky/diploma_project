from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.forum_posts_repository import find_post_by_id, increment_post_score
from app.repositories.forum_threads_repository import find_thread_by_id, increment_thread_score
from app.repositories.forum_votes_repository import (
    delete_vote,
    find_vote,
    insert_vote,
    update_vote_value,
)
from app.schemas.forum_vote import (
    ForumMyVoteResponse,
    ForumVotePayload,
    ForumVoteResponse,
)


def _build_vote_response(
    target_type: str,
    target_id: str,
    current_vote: int | None,
    score: int,
    message: str,
) -> ForumVoteResponse:
    return ForumVoteResponse(
        target_type=target_type,
        target_id=target_id,
        current_vote=current_vote,
        score=score,
        message=message,
    )


async def vote_thread(
    current_user_id: str,
    thread_id: str,
    payload: ForumVotePayload,
) -> ForumVoteResponse:
    thread = await find_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    if str(thread["user_id"]) == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot vote for your own thread")

    existing_vote = await find_vote(current_user_id, "thread", thread_id)

    if existing_vote is None:
        await insert_vote(
            user_id=current_user_id,
            target_type="thread",
            target_id=thread_id,
            value=payload.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await increment_thread_score(thread_id, payload.value)

        updated_thread = await find_thread_by_id(thread_id)
        if updated_thread is None:
            raise RuntimeError("Thread disappeared after voting")

        return _build_vote_response(
            target_type="thread",
            target_id=thread_id,
            current_vote=payload.value,
            score=updated_thread.get("score", 0),
            message="Vote saved",
        )

    old_value = existing_vote["value"]

    if old_value == payload.value:
        await delete_vote(current_user_id, "thread", thread_id)
        await increment_thread_score(thread_id, -old_value)

        updated_thread = await find_thread_by_id(thread_id)
        if updated_thread is None:
            raise RuntimeError("Thread disappeared after removing vote")

        return _build_vote_response(
            target_type="thread",
            target_id=thread_id,
            current_vote=None,
            score=updated_thread.get("score", 0),
            message="Vote removed",
        )

    await update_vote_value(
        user_id=current_user_id,
        target_type="thread",
        target_id=thread_id,
        value=payload.value,
        updated_at=datetime.now(UTC),
    )
    await increment_thread_score(thread_id, payload.value - old_value)

    updated_thread = await find_thread_by_id(thread_id)
    if updated_thread is None:
        raise RuntimeError("Thread disappeared after changing vote")

    return _build_vote_response(
        target_type="thread",
        target_id=thread_id,
        current_vote=payload.value,
        score=updated_thread.get("score", 0),
        message="Vote updated",
    )


async def vote_post(
    current_user_id: str,
    post_id: str,
    payload: ForumVotePayload,
) -> ForumVoteResponse:
    post = await find_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if str(post["user_id"]) == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot vote for your own post")

    existing_vote = await find_vote(current_user_id, "post", post_id)

    if existing_vote is None:
        await insert_vote(
            user_id=current_user_id,
            target_type="post",
            target_id=post_id,
            value=payload.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await increment_post_score(post_id, payload.value)

        updated_post = await find_post_by_id(post_id)
        if updated_post is None:
            raise RuntimeError("Post disappeared after voting")

        return _build_vote_response(
            target_type="post",
            target_id=post_id,
            current_vote=payload.value,
            score=updated_post.get("score", 0),
            message="Vote saved",
        )

    old_value = existing_vote["value"]

    if old_value == payload.value:
        await delete_vote(current_user_id, "post", post_id)
        await increment_post_score(post_id, -old_value)

        updated_post = await find_post_by_id(post_id)
        if updated_post is None:
            raise RuntimeError("Post disappeared after removing vote")

        return _build_vote_response(
            target_type="post",
            target_id=post_id,
            current_vote=None,
            score=updated_post.get("score", 0),
            message="Vote removed",
        )

    await update_vote_value(
        user_id=current_user_id,
        target_type="post",
        target_id=post_id,
        value=payload.value,
        updated_at=datetime.now(UTC),
    )
    await increment_post_score(post_id, payload.value - old_value)

    updated_post = await find_post_by_id(post_id)
    if updated_post is None:
        raise RuntimeError("Post disappeared after changing vote")

    return _build_vote_response(
        target_type="post",
        target_id=post_id,
        current_vote=payload.value,
        score=updated_post.get("score", 0),
        message="Vote updated",
    )


async def get_my_thread_vote(current_user_id: str, thread_id: str) -> ForumMyVoteResponse:
    thread = await find_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    vote = await find_vote(current_user_id, "thread", thread_id)

    return ForumMyVoteResponse(
        target_type="thread",
        target_id=thread_id,
        current_vote=vote["value"] if vote is not None else None,
    )


async def get_my_post_vote(current_user_id: str, post_id: str) -> ForumMyVoteResponse:
    post = await find_post_by_id(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    vote = await find_vote(current_user_id, "post", post_id)

    return ForumMyVoteResponse(
        target_type="post",
        target_id=post_id,
        current_vote=vote["value"] if vote is not None else None,
    )