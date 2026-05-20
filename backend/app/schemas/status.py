from typing import Literal

from pydantic import BaseModel

from app.schemas.item import MediaItem


ItemStatus = Literal["planned", "in_progress", "completed", "dropped"]


class StatusPayload(BaseModel):
    status: ItemStatus


class StatusActionResponse(BaseModel):
    message: str


class UserItemStatusResponse(BaseModel):
    item_id: str
    status: ItemStatus


class MediaItemWithStatus(MediaItem):
    status: ItemStatus