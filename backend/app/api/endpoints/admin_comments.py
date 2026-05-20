from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_admin
from app.schemas.comment import CommentActionResponse, CommentBaseResponse
from app.schemas.user import UserPublic
from app.services.comments_service import admin_delete_comment, get_recent_comments_for_admin

router = APIRouter(prefix="/admin/comments", tags=["admin-comments"])


@router.get("", response_model=list[CommentBaseResponse])
async def read_recent_comments_for_admin(
    limit: int = Query(default=100, ge=1, le=500),
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_recent_comments_for_admin(limit=limit)


@router.delete("/{comment_id}", response_model=CommentActionResponse)
async def delete_comment_by_admin(
    comment_id: str,
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await admin_delete_comment(current_admin, comment_id)