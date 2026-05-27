from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

    # Старе поле залишаємо для сумісності з поточним фронтом.
    # Backend буде сприймати його як "коментар, на який натиснули Reply".
    parent_comment_id: str | None = None

    # Нове бажане поле для нової логіки.
    # Це конкретний коментар, на який відповідаємо.
    reply_to_comment_id: str | None = None


class CommentUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentBaseResponse(BaseModel):
    id: str
    item_id: str
    user_id: str
    author_username: str
    author_avatar_id: str
    text: str

    # ID головного коментаря, під яким лежить відповідь.
    # Для top-level comment буде None.
    parent_comment_id: str | None

    # ID конкретного коментаря, на який натиснули Reply.
    reply_to_comment_id: str | None = None

    # ID користувача, якому відповіли.
    reply_to_user_id: str | None = None

    # Username користувача, якому відповіли.
    # Це фронт може показувати як "Replying to @username".
    reply_to_username: str | None = None

    created_at: datetime
    updated_at: datetime
    edited: bool


class CommentReplyResponse(CommentBaseResponse):
    pass


class CommentResponse(CommentBaseResponse):
    replies: list[CommentReplyResponse] = Field(default_factory=list)


class CommentActionResponse(BaseModel):
    message: str