from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.schemas.forum import ForumActionResponse, ForumPostBaseResponse, ForumThreadResponse
from app.schemas.user import UserPublic
from app.services.admin_forum_service import (
    admin_delete_post,
    admin_delete_thread,
    get_recent_posts_for_admin,
    get_recent_threads_for_admin,
)

router = APIRouter(prefix="/admin/forum", tags=["admin-forum"])


@router.get("/threads", response_model=list[ForumThreadResponse])
async def read_recent_threads_for_admin(
    limit: int = Query(default=100, ge=1, le=500),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_recent_threads_for_admin(limit=limit)


@router.get("/posts", response_model=list[ForumPostBaseResponse])
async def read_recent_posts_for_admin(
    limit: int = Query(default=100, ge=1, le=500),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_recent_posts_for_admin(limit=limit)


@router.delete("/threads/{thread_id}", response_model=ForumActionResponse)
async def delete_thread_by_admin(
    thread_id: str,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await admin_delete_thread(current_admin, thread_id)


@router.delete("/posts/{post_id}", response_model=ForumActionResponse)
async def delete_post_by_admin(
    post_id: str,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await admin_delete_post(current_admin, post_id)