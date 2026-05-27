from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.schemas.admin import (
    AdminForumPostsListResponse,
    AdminForumThreadsListResponse,
)
from app.schemas.forum import ForumActionResponse, ForumCategoryType
from app.schemas.user import UserPublic
from app.services.admin_forum_service import (
    admin_delete_post,
    admin_delete_thread,
)
from app.services.admin_service import (
    get_admin_forum_posts_list,
    get_admin_forum_threads_list,
)

router = APIRouter(prefix="/admin/forum", tags=["admin-forum"])


@router.get("/threads", response_model=AdminForumThreadsListResponse)
async def read_threads_for_admin(
    search: str | None = Query(default=None),
    category: ForumCategoryType | None = Query(default=None),
    user_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_admin_forum_threads_list(
        search=search,
        category=category,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )


@router.get("/posts", response_model=AdminForumPostsListResponse)
async def read_posts_for_admin(
    search: str | None = Query(default=None),
    thread_id: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_admin_forum_posts_list(
        search=search,
        thread_id=thread_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )


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