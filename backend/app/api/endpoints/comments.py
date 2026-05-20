from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.comment import (
    CommentActionResponse,
    CommentBaseResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.schemas.user import UserPublic
from app.services.comments_service import (
    create_comment_for_item,
    delete_own_comment,
    edit_own_comment,
    get_comments_for_item,
)

router = APIRouter(tags=["comments"])


@router.get("/items/{item_id}/comments", response_model=list[CommentResponse])
async def read_comments_for_item(
    item_id: str,
    limit: int = Query(default=100, ge=1, le=500),
):
    return await get_comments_for_item(item_id, limit=limit)


@router.post(
    "/items/{item_id}/comments",
    response_model=CommentBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment_endpoint(
    item_id: str,
    payload: CommentCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await create_comment_for_item(current_user, item_id, payload)


@router.put("/comments/{comment_id}", response_model=CommentBaseResponse)
async def update_comment_endpoint(
    comment_id: str,
    payload: CommentUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    return await edit_own_comment(current_user, comment_id, payload)


@router.delete("/comments/{comment_id}", response_model=CommentActionResponse)
async def delete_comment_endpoint(
    comment_id: str,
    current_user: UserPublic = Depends(get_current_user),
):
    return await delete_own_comment(current_user, comment_id)