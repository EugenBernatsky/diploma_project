from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    parent_comment_id: str | None = None


class CommentUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentBaseResponse(BaseModel):
    id: str
    item_id: str
    user_id: str
    author_username: str
    author_avatar_id: str
    text: str
    parent_comment_id: str | None
    created_at: datetime
    updated_at: datetime
    edited: bool


class CommentReplyResponse(CommentBaseResponse):
    pass


class CommentResponse(CommentBaseResponse):
    replies: list[CommentReplyResponse] = Field(default_factory=list)


class CommentActionResponse(BaseModel):
    message: str