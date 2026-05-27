from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.schemas.admin import AdminCommentsListResponse
from app.schemas.comment import CommentActionResponse
from app.schemas.user import UserPublic
from app.services.admin_service import get_admin_comments_list
from app.services.comments_service import admin_delete_comment

router = APIRouter(prefix="/admin/comments", tags=["admin-comments"])


@router.get("", response_model=AdminCommentsListResponse)
async def read_comments_for_admin(
    search: str | None = Query(default=None),
    item_id: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_admin_comments_list(
        search=search,
        item_id=item_id,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )


@router.delete("/{comment_id}", response_model=CommentActionResponse)
async def delete_comment_by_admin(
    comment_id: str,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await admin_delete_comment(current_admin, comment_id)