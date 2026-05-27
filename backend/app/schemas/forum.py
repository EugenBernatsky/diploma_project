from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ForumCategoryType = Literal["movie", "series", "book", "custom"]


class ForumThreadCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    text: str = Field(min_length=1, max_length=5000)
    category_type: ForumCategoryType
    custom_category: str | None = Field(default=None, min_length=2, max_length=50)

    @model_validator(mode="after")
    def validate_category(self):
        if self.category_type == "custom":
            if not self.custom_category or not self.custom_category.strip():
                raise ValueError("custom_category is required when category_type='custom'")
            self.custom_category = self.custom_category.strip()
        else:
            self.custom_category = None
        return self


class ForumThreadUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    text: str = Field(min_length=1, max_length=5000)
    category_type: ForumCategoryType
    custom_category: str | None = Field(default=None, min_length=2, max_length=50)

    @model_validator(mode="after")
    def validate_category(self):
        if self.category_type == "custom":
            if not self.custom_category or not self.custom_category.strip():
                raise ValueError("custom_category is required when category_type='custom'")
            self.custom_category = self.custom_category.strip()
        else:
            self.custom_category = None
        return self


class ForumPostCreate(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

    # Старе поле залишаємо для сумісності з поточним фронтом.
    # Backend буде сприймати його як "пост, на який натиснули Reply".
    parent_post_id: str | None = None

    # Нове бажане поле для нової логіки.
    # Це конкретний пост, на який відповідаємо.
    reply_to_post_id: str | None = None

class ForumPostUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class ForumThreadResponse(BaseModel):
    id: str
    user_id: str
    author_username: str
    author_avatar_id: str
    title: str
    text: str
    category_type: ForumCategoryType
    custom_category: str | None
    score: int
    replies_count: int
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    edited: bool


class ForumPostBaseResponse(BaseModel):
    id: str
    thread_id: str
    user_id: str
    author_username: str
    author_avatar_id: str
    text: str
    score: int

    # ID головного поста, під яким лежить відповідь.
    # Для top-level post буде None.
    parent_post_id: str | None

    # ID конкретного поста, на який натиснули Reply.
    reply_to_post_id: str | None = None

    # ID користувача, якому відповіли.
    reply_to_user_id: str | None = None

    # Username користувача, якому відповіли.
    reply_to_username: str | None = None

    created_at: datetime
    updated_at: datetime
    edited: bool


class ForumPostReplyResponse(ForumPostBaseResponse):
    pass


class ForumPostResponse(ForumPostBaseResponse):
    replies: list[ForumPostReplyResponse] = Field(default_factory=list)


class ForumActionResponse(BaseModel):
    message: str