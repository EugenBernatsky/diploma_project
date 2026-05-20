from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.forum import (
    ForumActionResponse,
    ForumPostBaseResponse,
    ForumPostCreate,
    ForumPostResponse,
    ForumPostUpdate,
    ForumThreadCreate,
    ForumThreadResponse,
    ForumThreadUpdate,
)
from app.schemas.forum_vote import ForumMyVoteResponse, ForumVotePayload, ForumVoteResponse
from app.schemas.user import UserPublic
from app.services.forum_service import (
    create_thread_forum,
    create_thread_post,
    delete_own_post,
    delete_own_thread,
    edit_own_post,
    edit_own_thread,
    get_thread,
    get_thread_posts,
    get_threads_list,
)
from app.services.forum_votes_service import (
    get_my_post_vote,
    get_my_thread_vote,
    vote_post,
    vote_thread,
)

router = APIRouter(prefix="/forum", tags=["forum"])

ThreadSort = Literal["activity", "newest", "score"]
ThreadCategoryType = Literal["movie", "series", "book", "custom"]

@router.get("/threads", response_model=list[ForumThreadResponse])
async def read_threads(
    limit: int = Query(default=100, ge=1, le=500),
    sort: ThreadSort = Query(default="activity"),
    category_type: ThreadCategoryType | None = Query(default=None),
    custom_category: str | None = Query(default=None, min_length=2, max_length=50),
):
    return await get_threads_list(
        limit=limit,
        sort_by=sort,
        category_type=category_type,
        custom_category=custom_category,
    )


@router.post("/threads", response_model=ForumThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread_endpoint(
    payload: ForumThreadCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await create_thread_forum(current_user, payload)


@router.get("/threads/{thread_id}", response_model=ForumThreadResponse)
async def read_thread(thread_id: str):
    return await get_thread(thread_id)


@router.put("/threads/{thread_id}", response_model=ForumThreadResponse)
async def update_thread_endpoint(
    thread_id: str,
    payload: ForumThreadUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await edit_own_thread(current_user, thread_id, payload)


@router.delete("/threads/{thread_id}", response_model=ForumActionResponse)
async def delete_thread_endpoint(
    thread_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await delete_own_thread(current_user, thread_id)


@router.put("/threads/{thread_id}/vote", response_model=ForumVoteResponse)
async def vote_thread_endpoint(
    thread_id: str,
    payload: ForumVotePayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await vote_thread(current_user.id, thread_id, payload)


@router.get("/threads/{thread_id}/my-vote", response_model=ForumMyVoteResponse)
async def read_my_thread_vote(
    thread_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_my_thread_vote(current_user.id, thread_id)


@router.get("/threads/{thread_id}/posts", response_model=list[ForumPostResponse])
async def read_thread_posts(
    thread_id: str,
    limit: int = Query(default=200, ge=1, le=1000),
):
    return await get_thread_posts(thread_id, limit=limit)


@router.post("/threads/{thread_id}/posts", response_model=ForumPostBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_post_endpoint(
    thread_id: str,
    payload: ForumPostCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await create_thread_post(current_user, thread_id, payload)


@router.put("/posts/{post_id}", response_model=ForumPostBaseResponse)
async def update_post_endpoint(
    post_id: str,
    payload: ForumPostUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await edit_own_post(current_user, post_id, payload)


@router.delete("/posts/{post_id}", response_model=ForumActionResponse)
async def delete_post_endpoint(
    post_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await delete_own_post(current_user, post_id)


@router.put("/posts/{post_id}/vote", response_model=ForumVoteResponse)
async def vote_post_endpoint(
    post_id: str,
    payload: ForumVotePayload,
    current_user: UserPublic = Depends(get_current_user),
):
    return await vote_post(current_user.id, post_id, payload)


@router.get("/posts/{post_id}/my-vote", response_model=ForumMyVoteResponse)
async def read_my_post_vote(
    post_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await get_my_post_vote(current_user.id, post_id)